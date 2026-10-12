#!/usr/bin/env python3
"""import-prompts-chat.py — 从 prompts.chat 批量导入提示词为 PWS 关键词格式。

数据来源: https://prompts.chat/prompts.csv (CC0 Public Domain)
依赖: 仅标准库 + requests

# 已弃用：prompts.chat 数据源定位为 ChatGPT 文本对话提示词，与 PWS 图像/视频生成定位不符。2026-10 移除。
# 一次性脚本，已执行完毕，请勿重复运行。
"""

import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

# 提高 CSV 字段大小限制（prompts.chat 有超长行）
csv.field_size_limit(10**8)

CSV_URL = "https://prompts.chat/prompts.csv"
CACHE_DIR = ".cache"
CACHE_FILE = os.path.join(CACHE_DIR, "prompts-chat.csv")
OUTPUT_FILE = "keywords/categories/_pending_review.json"
CACHE_TTL_SECONDS = 24 * 3600  # 缓存 24 小时

# 分类启发式映射规则
CATEGORY_RULES = {
    "character": [
        "portrait", "face", "character", "person", "people", "woman",
        "man", "girl", "boy", "child", "children", "self-portrait",
        "headshot", "avatar", "figure", "model", "subject", "people",
        "personality", "persona", "biography", "roleplay", "rp",
    ],
    "lighting": [
        "light", "glow", "shadow", "shadows", "illumination",
        "bloom", "volumetric", "cinematic light", "natural light",
        "studio lighting", "backlit", "rim light", "ambient light",
        "lighting", "brightness", "contrast", "hdr", "high dynamic",
    ],
    "composition": [
        "shot", "camera", "angle", "lens", "view", "perspective",
        "framing", "close-up", "closeup", "medium shot", "wide angle",
        "fisheye", "macro", "bokeh", "depth of field", "dof",
        "rule of thirds", "golden ratio", "leading lines", "symmetry",
        "panoramic", "aerial", "drone", "bird's eye", "low angle",
        "high angle", "dutch angle", "tilt-shift", "isometric",
    ],
    "styles": [
        "style", "render", "art", "painting", "illustration", "sketch",
        "drawing", "watercolor", "oil painting", "anime", "manga",
        "realistic", "photorealistic", "surreal", "abstract",
        "minimalist", "baroque", "rococo", "impressionism",
        "cubism", "pop art", "art deco", "art nouveau", "pixel art",
        "chibi", "semirealism", "concept art", "digital art",
        "vector art", "3d render", "isometric view", "flat design",
    ],
}


def classify(act: str, prompt: str) -> str:
    """基于 act 和 prompt 关键词启发式分类。"""
    text = (act + " " + prompt).lower()
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in text:
                return category
    return "uncategorized"


def make_id(category: str, term: str) -> str:
    """生成 PWS 格式 id: {category}_prompts_chat_{md5(term)[:8]}"""
    md5 = hashlib.md5(term.encode("utf-8")).hexdigest()[:8]
    return f"{category}_prompts_chat_{md5}"


def download_csv() -> str:
    """下载 CSV，使用本地缓存（24 小时有效）。"""
    if os.path.exists(CACHE_FILE):
        mtime = os.path.getmtime(CACHE_FILE)
        age = (datetime.now(timezone.utc).timestamp() - mtime)
        if age < CACHE_TTL_SECONDS:
            print(f"[cache] Using cached {CACHE_FILE} (age={int(age)}s)")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print(f"[cache] Cache expired (age={int(age)}s > {CACHE_TTL_SECONDS}s)")

    try:
        import requests
    except ImportError:
        print("ERROR: 'requests' is required. Install with: pip install requests", file=sys.stderr)
        sys.exit(1)

    print(f"[download] Fetching {CSV_URL} ...")
    resp = requests.get(CSV_URL, timeout=120)
    resp.raise_for_status()

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(resp.text)

    print(f"[download] Saved to {CACHE_FILE} ({len(resp.text)} bytes)")
    return resp.text


def parse_csv(csv_text: str) -> list[dict]:
    """解析 CSV，返回 (act, prompt, type) 元组列表。"""
    reader = csv.DictReader(csv_text.splitlines())
    results = []
    for row in reader:
        act = (row.get("act") or "").strip()
        prompt = (row.get("prompt") or "").strip()
        ptype = (row.get("type") or "").strip().upper()
        results.append({"act": act, "prompt": prompt, "type": ptype})
    return results


def filter_entries(entries: list[dict]):
    """筛选: type == TEXT 且 prompt 长度 5-200 字符。"""
    filtered = []
    skipped_type = 0
    skipped_length = 0

    for e in entries:
        if e["type"] != "TEXT":
            skipped_type += 1
            continue
        plen = len(e["prompt"])
        if plen < 5 or plen > 200:
            skipped_length += 1
            continue
        filtered.append(e)

    return filtered, skipped_type, skipped_length


def build_keywords(filtered: list[dict]) -> list[dict]:
    """将筛选后的条目转换为 PWS keyword 格式。"""
    keywords = []

    for e in filtered:
        prompt = e["prompt"]
        act = e.get("act", "")

        category = classify(act, prompt)
        subcategory = "prompts_chat"

        kw = {
            "id": make_id(category, prompt),
            "term": prompt,
            "term_zh": "",
            "category": category,
            "subcategory": subcategory,
            "weight": 0.5,
            "score": 0.5,
            "source": "f/prompts.chat CC0",
            "compatibility": ["sdxl", "midjourney", "flux"],
            "is_negative": False,
            "lifecycle": "draft",
        }
        keywords.append(kw)

    return keywords


def write_output(keywords: list[dict]):
    """写入 _pending_review.json。"""
    os.makedirs("keywords/categories", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=2, ensure_ascii=False)
        f.write("\n")


def print_report(total_downloaded: int, filtered_count: int, skipped_type: int,
                 skipped_length: int, keywords: list[dict]):
    """打印统计报告。"""
    # 分类分布
    cat_dist = {}
    for kw in keywords:
        c = kw["category"]
        cat_dist[c] = cat_dist.get(c, 0) + 1

    print("\n" + "=" * 60)
    print("PROMPTS.CHAT IMPORT REPORT")
    print("=" * 60)
    print(f"Total downloaded (CSV rows): {total_downloaded}")
    print(f"Skipped (non-TEXT type):     {skipped_type}")
    print(f"Skipped (length outside 5-200): {skipped_length}")
    print(f"Filtered and retained:       {filtered_count}")
    print(f"Keywords generated:          {len(keywords)}")

    print("\nCategory distribution:")
    for cat in sorted(cat_dist.keys()):
        print(f"  {cat:20s}: {cat_dist[cat]}")

    print(f"\nOutput file: {OUTPUT_FILE}")
    print("=" * 60)


def main():
    # 1. 下载/读取 CSV
    csv_text = download_csv()

    # 2. 解析 CSV
    entries = parse_csv(csv_text)
    total_downloaded = len(entries)

    # 3. 筛选
    filtered, skipped_type, skipped_length = filter_entries(entries)

    # 4. 构建关键词
    keywords = build_keywords(filtered)

    # 5. 写入输出文件
    write_output(keywords)

    # 6. 报告
    print_report(total_downloaded, len(filtered), skipped_type, skipped_length, keywords)


if __name__ == "__main__":
    main()
