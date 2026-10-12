#!/usr/bin/env python3
"""import-shuixian.py — 从 shuixian-prompts 提取原子化中文标签，补充 term_zh。

数据来源: BaYue-SYJ/shuixian-prompts (GitHub)
依赖: 仅标准库

# 已弃用：shuixian-prompts 为提示词案例展示库，非关键词数据库。2026-10 评估后放弃。
# 一次性脚本，已执行完毕，请勿重复运行。
"""

import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter


SHUIXIAN_DIR = "/tmp/shuixian-prompts"

# 使用 list.part*.json（有 themes/styles）和 prompts.part*.json（有 category）
LIST_FILES = [
    "shuixian-unified/data/list.part1.json",
    "shuixian-unified/data/list.part2.json",
    "shuixian-unified/data/list.part3.json",
]
PROMPTS_FILES = [
    "shuixian-unified/data/prompts.part1.json",
    "shuixian-unified/data/prompts.part2.json",
    "shuixian-unified/data/prompts.part3.json",
]

OUTPUT_DIR = "keywords/categories"
PENDING_FILE = os.path.join(OUTPUT_DIR, "_pending_review.json")
SUPPLEMENT_FILE = os.path.join(OUTPUT_DIR, "term_zh_supplement.json")

# 分类映射关键词（标签→PWS 分类）
CATEGORY_KEYWORDS = {
    "composition": ["海报", "设计", "排版", "构图", "视觉", "宣传"],
    "character": ["人像", "人物", "模特", "角色", "写真", "肖像"],
    "scene": ["风景", "场景", "环境", "建筑", "城市", "自然"],
    "styles": ["风格", "艺术", "插画", "动漫", "漫画", "写实", "水彩"],
}

# 停用词表（无实际图像意义的常见中文词）
STOPWORDS = {
    "一张", "画面", "内容", "快照", "作品", "效果", "感觉", "元素",
    "部分", "所有", "各种", "整个", "完全", "整体", "全部", "方面",
    "东西", "什么", "怎么", "这个", "那个",
    "以上", "以下", "其中", "之间", "之内", "之外", "之上", "之下",
    "里面", "外面", "上面", "下面", "左边", "右边", "中间",
    "每个", "任何", "某些", "整个", "全部",
}


def classify_from_tag(tag: str) -> str:
    """基于标签本身判断分类。"""
    for pws_cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in tag:
                return pws_cat
    return "uncategorized"


def is_valid_tag(tag: str) -> bool:
    """检查标签是否符合原子化关键词标准（2-10 纯中文字符，非停用词）。"""
    tag = str(tag).strip()
    if not tag:
        return False
    if len(tag) < 2 or len(tag) > 10:
        return False
    if not re.match(r'^[\u4e00-\u9fff]+$', tag):
        return False  # 含非中文字符（数字、英文、标点）
    if tag in STOPWORDS:
        return False
    return True


def load_existing_term_zh() -> dict[str, str]:
    """加载现有 PWS 库中所有 term_zh 值，返回 {term_zh: id} 映射。"""
    existing = {}
    for f in sorted(glob.glob("keywords/categories/*.json")):
        basename = os.path.basename(f)
        if basename in ("_pending_review.json", "term_zh_supplement.json"):
            continue
        with open(f) as fh:
            data = json.load(fh)
        for kw in data:
            tz = kw.get("term_zh", "").strip()
            if tz and tz not in existing:
                existing[tz] = kw["id"]
    return existing


def make_id(category: str, term_zh: str) -> str:
    """生成 id: {category}_shuixian_{md5(term_zh)[:8]}"""
    md5 = hashlib.md5(term_zh.encode("utf-8")).hexdigest()[:8]
    return f"{category}_shuixian_{md5}"


def main():
    print(f"[load] Loading existing term_zh from PWS library...")
    existing_term_zh = load_existing_term_zh()
    print(f"[load] Existing term_zh values: {len(existing_term_zh)}")

    # 读取 list 数据（有 themes/styles）
    all_items = []
    for pf in LIST_FILES:
        fpath = os.path.join(SHUIXIAN_DIR, pf)
        if not os.path.exists(fpath):
            print(f"[warn] {fpath} not found, skipping")
            continue
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        all_items.extend(data)

    # 读取 prompts 数据（有 category）
    all_categories = []
    for pf in PROMPTS_FILES:
        fpath = os.path.join(SHUIXIAN_DIR, pf)
        if not os.path.exists(fpath):
            print(f"[warn] {fpath} not found, skipping")
            continue
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            cat = (item.get("category") or "").strip()
            if cat:
                all_categories.append(cat)

    print(f"\n[shuixian] Total items (list files): {len(all_items)}")
    print(f"[shuixian] Total category entries (prompts files): {len(all_categories)}")

    # 提取标签：themes + styles（从 list files）
    all_tags = []
    filter_stats = {"valid": 0, "stopword": 0, "length": 0, "non_chinese": 0}

    for item in all_items:
        title = (item.get("title") or "").strip()
        themes = item.get("themes") or []
        styles = item.get("styles") or []

        # 从 themes 和 styles 提取标签
        raw_tags = list(themes) + list(styles)

        # 如果 title 是纯中文且长度≥3，也作为候选
        if title and re.match(r'^[\u4e00-\u9fff]{3,}$', title):
            raw_tags.append(title)

        for tag in raw_tags:
            if not is_valid_tag(tag):
                if len(str(tag)) < 2 or len(str(tag)) > 10:
                    filter_stats["length"] += 1
                elif str(tag) in STOPWORDS:
                    filter_stats["stopword"] += 1
                elif not re.match(r'^[\u4e00-\u9fff]+$', str(tag)):
                    filter_stats["non_chinese"] += 1
                else:
                    filter_stats["stopword"] += 1
                continue

            all_tags.append(tag)
            filter_stats["valid"] += 1

    # 从 category 字段提取纯中文子分类名（长度 2-10）
    for cat in all_categories:
        if is_valid_tag(cat):
            all_tags.append(cat)
            filter_stats["valid"] += 1
        else:
            if len(str(cat)) < 2 or len(str(cat)) > 10:
                filter_stats["length"] += 1
            elif not re.match(r'^[\u4e00-\u9fff]+$', str(cat)):
                filter_stats["non_chinese"] += 1

    # 统计频次，去重后保留出现≥2次的标签（确保不是噪声）
    tag_freq = Counter(all_tags)

    unique_tags = {}
    for tag, count in tag_freq.most_common():
        if count >= 2 and is_valid_tag(tag):
            unique_tags[tag] = count

    print(f"\n[extraction] Total valid tags (freq≥2): {len(unique_tags)}")
    print(f"Filtered out: stopword={filter_stats['stopword']}, length={filter_stats['length']}, non_chinese={filter_stats['non_chinese']}")

    # 分类和输出
    supplement_items = []  # 匹配到已有 term_zh 的补充记录
    new_items = []  # 全新候选

    for tag, count in unique_tags.items():
        pws_category = classify_from_tag(tag)

        if tag in existing_term_zh:
            supplement_items.append({
                "existing_id": existing_term_zh[tag],
                "term_zh": tag,
                "occurrence_count": count,
            })
        else:
            kw = {
                "id": make_id(pws_category, tag),
                "term": "",
                "term_zh": tag,
                "category": pws_category,
                "subcategory": tag,  # 原子化标签本身作为 subcategory
                "weight": 0.5,
                "score": 0.5,
                "source": "BaYue-SYJ/shuixian-prompts",
                "compatibility": ["sdxl", "midjourney"],
                "is_negative": False,
                "needs_en_translation": True,
                "occurrence_count": count,
            }
            new_items.append(kw)

    # 写入 _pending_review.json
    print(f"\n[output] Writing {len(new_items)} new candidates to {PENDING_FILE}")
    existing_pending = []
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE) as f:
            existing_pending = json.load(f)
    merged_pending = existing_pending + new_items
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_pending, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 写入 term_zh_supplement.json
    print(f"[output] Writing {len(supplement_items)} supplements to {SUPPLEMENT_FILE}")
    existing_supplement = []
    if os.path.exists(SUPPLEMENT_FILE):
        with open(SUPPLEMENT_FILE) as f:
            existing_supplement = json.load(f)
    merged_supplement = existing_supplement + supplement_items
    with open(SUPPLEMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_supplement, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 统计报告
    new_unique = len(new_items)

    print("\n" + "=" * 60)
    print("SHUIXIAN PROMPTS IMPORT REPORT (ATOMIC TAGS ONLY)")
    print("=" * 60)
    print(f"Data files processed: {len(LIST_FILES)} list + {len(PROMPTS_FILES)} prompts")
    print(f"Total items processed: {len(all_items)} + {len(all_categories)} categories")
    print(f"Valid tags extracted (freq≥2): {len(unique_tags)}")
    total_filtered = filter_stats['stopword'] + filter_stats['length'] + filter_stats['non_chinese']
    print(f"Filtered out: {total_filtered}")
    print(f"  - stopword: {filter_stats['stopword']}")
    print(f"  - length out of range: {filter_stats['length']}")
    print(f"  - non-Chinese/contains symbols: {filter_stats['non_chinese']}")
    print(f"Matched to existing PWS term_zh: {len(supplement_items)}")
    print(f"New candidates (needs_en_translation): {new_unique}")

    # 检查产出规模
    if new_unique > 3000:
        print(f"\n⚠️ WARNING: {new_unique} new candidates exceeds 3000 target!")
    elif 500 <= new_unique <= 3000:
        print(f"\n✓ Within target range (500-3000)")
    else:
        print(f"\n⚠️ Below minimum 500 (only {new_unique})")

    print("\nCategory distribution (new candidates):")
    new_cat_dist = {}
    for kw in new_items:
        c = kw["category"]
        new_cat_dist[c] = new_cat_dist.get(c, 0) + 1
    for cat in sorted(new_cat_dist.keys()):
        print(f"  {cat:20s}: {new_cat_dist[cat]}")

    print(f"\nTop 30 tags by frequency:")
    for tag, count in sorted(unique_tags.items(), key=lambda x: -x[1])[:30]:
        print(f"  {tag}: {count}")

    print(f"\nOutput files:")
    print(f"  {PENDING_FILE} ({len(new_items)} new candidates)")
    print(f"  {SUPPLEMENT_FILE} ({len(supplement_items)} supplements)")
    print("=" * 60)


if __name__ == "__main__":
    main()
