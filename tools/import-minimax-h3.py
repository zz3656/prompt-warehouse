#!/usr/bin/env python3
"""import-minimax-h3.py — 从 BeatAPI/awesome-minimax-h3-prompts 提取视频专用关键词。

数据来源: BeatAPI/awesome-minimax-h3-prompts (GitHub)
依赖: 仅标准库

# 一次性脚本，已执行完毕，请勿重复运行。
"""

import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter


SHUIXIAN_DIR = "/tmp/minimax-h3-prompts"

OUTPUT_DIR = "keywords/categories"
PENDING_FILE = os.path.join(OUTPUT_DIR, "_pending_review.json")

# 视频关键词术语表
VIDEO_TERMS = {
    "camera_motion": [
        "dolly in", "dolly out", "zoom in", "zoom out", "pan left", "pan right",
        "tilt up", "tilt down", "tracking shot", "orbit camera", "whip pan",
        "crane shot", "low angle", "high angle", "bird's eye", "aerial shot",
        "handheld", "steady cam", "push in", "pull back", "arc shot",
        "slider shot", "dutch angle", "rack focus", "follow cam", "fpv drone",
        "slow pan", "fast pan", "smooth pan", "tilt forward", "tilt backward",
        "panning shot", "tracking camera", "orbiting shot", "helicopter shot",
        "jib shot", "stabilized shot", "dynamic camera", "fluid motion",
        "floating camera", "gliding shot", "sweeping shot", "spinning camera"
    ],
    "transition": [
        "match cut", "seamless transition", "dissolve", "whip pan transition",
        "cross dissolve", "fade in", "fade out", "jump cut", "smash cut",
        "iris out", "wipe transition", "morphing", "split screen", "lens flare",
        "light leak", "flash transition", "blur transition", "spin cut",
        "infinite zoom", "speed ramp", "time warp"
    ],
    "lens": [
        "24mm", "35mm", "50mm", "85mm", "100mm", "135mm", "200mm",
        "prime lens", "wide-angle", "macro lens", "fisheye", "anamorphic",
        "telephoto", "tilt-shift", "bokeh", "depth of field", "dof",
        "shallow focus", "sharp focus", "soft focus", "cinema lens",
        "anamorphic lens", "prime glass", "fast lens"
    ],
    "lighting": [
        "golden hour", "blue hour", "volumetric lighting", "rim light",
        "neon glow", "backlit", "chiaroscuro", "softbox lighting",
        "studio lighting", "natural light", "ambient light", "dramatic lighting",
        "moody lighting", "high key", "low key", "cinematic lighting",
        "rembrandt lighting", "butterfly lighting", "silhouette",
        "contre-jour", "god rays", "caustics", "subsurface scattering",
        "practical lighting"
    ],
    "scene": [
        "cyberpunk city", "rainy street", "stone corridor", "bamboo forest",
        "ancient temple", "modern office", "kitchen at dusk", "underground nightclub",
        "luxury showroom", "desert runway", "mountain lake", "urban alley",
        "rooftop bar", "subway station", "beach at sunset", "snowy mountain",
        "tropical island", "abandoned building", "glass conservatory",
        "industrial warehouse", "medieval castle", "futuristic city",
        "suburban street", "countryside road", "city skyline"
    ],
    "time_edit": [
        "slow motion", "time-lapse", "continuous shot", "speed ramp",
        "motion blur", "freeze frame", "stop motion", "hyperlapse",
        "timelapse", "frame-by-frame", "fps", "24fps", "30fps", "60fps",
        "high frame rate", "low frame rate", "frame interpolation"
    ],
    "style": [
        "cinematic", "photorealistic", "anime", "2D cel-shaded",
        "3D rendered", "stop-motion", "live-action", "documentary style",
        "noir", "surreal", "abstract", "minimalist", "vintage film",
        "film grain", "film look", "color graded", "HDR", "4K resolution",
        "8K resolution", "film stock", "analog", "digital", "VHS style",
        "VFX heavy", "CGI"
    ],
}

# 分类映射（术语类型 → PWS 分类）
TERM_TO_CATEGORY = {
    "camera_motion": {"composition": ["composition", "camera-motions", "angles"]},
    "transition": {"transitions": ["transitions"]},
    "lens": {"composition": ["composition", "lens"]},
    "lighting": {"lighting": ["lighting"]},
    "scene": {"scene": ["scene", "backdrop", "setting"]},
    "time_edit": {"temporal": ["temporal", "speed", "freeze"]},
    "style": {"styles": ["styles", "quality"]},
}

# 术语到子分类的启发式映射（用于更精确的子分类）
SUBCATEGORY_MAP = {
    "camera_motion": {
        "dolly in": "push-in", "dolly out": "pull-out", "zoom in": "zoom-in",
        "zoom out": "zoom-out", "pan left": "panning", "pan right": "panning",
        "tilt up": "tilting", "tilt down": "tilting", "tracking shot": "tracking",
        "orbit camera": "orbiting", "whip pan": "whip-pan", "crane shot": "crane",
        "low angle": "angles", "high angle": "angles", "bird's eye": "aerial",
        "aerial shot": "aerial", "handheld": "handheld", "steady cam": "stabilized",
        "push in": "push-in", "pull back": "pull-out", "arc shot": "orbiting",
        "slider shot": "stabilized", "dutch angle": "angles", "rack focus": "focus-pull",
        "follow cam": "tracking", "fpv drone": "aerial", "slow pan": "panning",
        "fast pan": "panning", "smooth pan": "panning", "tilt forward": "tilting",
        "tilt backward": "tilting", "panning shot": "panning", "tracking camera": "tracking",
        "orbiting shot": "orbiting", "helicopter shot": "aerial", "jib shot": "crane",
        "stabilized shot": "stabilized", "dynamic camera": "dynamic", "fluid motion": "stabilized",
        "floating camera": "stabilized", "gliding shot": "stabilized",
        "sweeping shot": "panning", "spinning camera": "orbiting"
    },
    "transition": {
        "match cut": "jump-cut", "seamless transition": "seamless",
        "dissolve": "cross-dissolve", "whip pan transition": "whip-pan",
        "cross dissolve": "cross-dissolve", "fade in": "fade-in",
        "fade out": "fade-out", "jump cut": "jump-cut", "smash cut": "jump-cut",
        "iris out": "fade-out", "wipe transition": "wipe", "morphing": "morph",
        "split screen": "split-screen", "lens flare": "lens-flare",
        "light leak": "light-leak", "flash transition": "flash-cut",
        "blur transition": "blur-cut", "spin cut": "spin",
        "infinite zoom": "infinite-zoom", "speed ramp": "speed-ramp",
        "time warp": "time-warp"
    },
    "lens": {
        "24mm": "wide-angle", "35mm": "wide-angle", "50mm": "prime",
        "85mm": "portrait", "100mm": "macro", "135mm": "telephoto", "200mm": "telephoto",
        "prime lens": "prime", "wide-angle": "wide-angle", "macro lens": "macro",
        "fisheye": "fisheye", "anamorphic": "anamorphic", "telephoto": "telephoto",
        "tilt-shift": "tilt-shift", "bokeh": "depth-of-field",
        "depth of field": "depth-of-field", "dof": "depth-of-field",
        "shallow focus": "depth-of-field", "sharp focus": "focus",
        "soft focus": "focus", "cinema lens": "anamorphic",
        "anamorphic lens": "anamorphic", "prime glass": "prime", "fast lens": "prime"
    },
    "lighting": {
        "golden hour": "time-of-day", "blue hour": "time-of-day",
        "volumetric lighting": "atmospheric", "rim light": "dramatic",
        "neon glow": "neon", "backlit": "backlighting", "chiaroscuro": "dramatic",
        "softbox lighting": "studio", "studio lighting": "studio",
        "natural light": "time-of-day", "ambient light": "atmospheric",
        "dramatic lighting": "dramatic", "moody lighting": "atmospheric",
        "high key": "studio", "low key": "dramatic", "cinematic lighting": "dramatic",
        "rembrandt lighting": "dramatic", "butterfly lighting": "portrait",
        "silhouette": "silhouette", "contre-jour": "time-of-day",
        "god rays": "atmospheric", "caustics": "atmospheric",
        "subsurface scattering": "rendering", "practical lighting": "atmospheric"
    },
    "scene": {
        "cyberpunk city": "urban", "rainy street": "urban", "stone corridor": "interior",
        "bamboo forest": "nature", "ancient temple": "architecture", "modern office": "interior",
        "kitchen at dusk": "interior", "underground nightclub": "urban",
        "luxury showroom": "commercial", "desert runway": "landscape",
        "mountain lake": "landscape", "urban alley": "urban",
        "rooftop bar": "urban", "subway station": "urban",
        "beach at sunset": "landscape", "snowy mountain": "landscape",
        "tropical island": "landscape", "abandoned building": "architecture",
        "glass conservatory": "architecture", "industrial warehouse": "commercial",
        "medieval castle": "architecture", "futuristic city": "urban",
        "suburban street": "suburban", "countryside road": "landscape",
        "city skyline": "urban"
    },
    "time_edit": {
        "slow motion": "slow-motion", "time-lapse": "time-lapse",
        "continuous shot": "long-take", "speed ramp": "speed-ramp",
        "motion blur": "motion-blur", "freeze frame": "freeze-frame",
        "stop motion": "stop-motion", "hyperlapse": "time-lapse",
        "timelapse": "time-lapse", "frame-by-frame": "stop-motion",
        "fps": "frame-rate", "24fps": "frame-rate", "30fps": "frame-rate",
        "60fps": "frame-rate", "high frame rate": "frame-rate",
        "low frame rate": "frame-rate", "frame interpolation": "interpolation"
    },
    "style": {
        "cinematic": "cinematic", "photorealistic": "realism",
        "anime": "anime", "2D cel-shaded": "anime", "3D rendered": "3d-render",
        "stop-motion": "stop-motion", "live-action": "realism",
        "documentary style": "documentary", "noir": "noir", "surreal": "surreal",
        "abstract": "abstract", "minimalist": "minimalism", "vintage film": "retro",
        "film grain": "retro", "film look": "cinematic", "color graded": "post-process",
        "HDR": "technical", "4K resolution": "technical", "8K resolution": "technical",
        "film stock": "retro", "analog": "retro", "digital": "technical",
        "VHS style": "retro", "VFX heavy": "vfx", "CGI": "3d-render"
    },
}

# 停用词（纯通用词，无实际图像意义）
STOPWORDS = {
    "cinematic", "digital", "dof", "fps", "HDR", "CGI", "anime",
    "abstract", "noir", "surreal", "minimalist", "analog",
    "live-action", "film grain", "stop motion", "motion blur",
}


def classify(term: str, term_type: str) -> tuple[str, str]:
    """返回 (category, subcategory)。"""
    # 子分类
    sub_map = SUBCATEGORY_MAP.get(term_type, {})
    sub = sub_map.get(term.lower(), term_type)

    # 主分类
    cat_map = TERM_TO_CATEGORY.get(term_type, {})
    for cat in cat_map:
        return (cat, sub)
    return ("uncategorized", term_type)


def make_id(category: str, term: str) -> str:
    """生成 id: {category}_minimax_h3_{md5(term)[:8]}"""
    md5 = hashlib.md5(term.encode("utf-8")).hexdigest()[:8]
    return f"{category}_minimax_h3_{md5}"


def load_existing_terms() -> tuple[set[str], set[str]]:
    """加载现有 PWS 库中所有 term 和 term_zh，返回 (set[term], set[term_zh])。"""
    existing_terms = set()
    existing_zh = set()
    for f in sorted(glob.glob("keywords/categories/*.json")):
        basename = os.path.basename(f)
        if basename in ("_pending_review.json", "term_zh_supplement.json"):
            continue
        with open(f) as fh:
            data = json.load(fh)
        for kw in data:
            t = (kw.get("term") or "").strip().lower()
            tz = (kw.get("term_zh") or "").strip().lower()
            if t:
                existing_terms.add(t)
            if tz:
                existing_zh.add(tz)
    return existing_terms, existing_zh


def main():
    repo_dir = "/tmp/awesome-minimax-h3-prompts"
    json_files = glob.glob(os.path.join(repo_dir, "prompts", "*.json"))

    if not json_files:
        print(f"ERROR: no JSON files found in {os.path.join(repo_dir, 'prompts/')}", file=sys.stderr)
        sys.exit(1)

    print(f"[load] Loading existing PWS terms (term + term_zh)...")
    existing_terms, existing_zh = load_existing_terms()
    print(f"[load] Existing terms: {len(existing_terms)}, existing term_zh: {len(existing_zh)}")

    # 读取所有 JSON 数据
    all_items = []
    for fpath in sorted(json_files):
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        all_items.append(data)

    print(f"\n[minimax-h3] Total entries: {len(all_items)}")

    # 匹配术语
    matched_terms = []  # (term_type, term_text, category_raw)
    filter_stats = {"matched": 0, "existing": 0, "stopword": 0, "length": 0}

    for item in all_items:
        prompt = (item.get("prompt") or "").lower()

        for term_type, terms in VIDEO_TERMS.items():
            for t in terms:
                if t.lower() in prompt:
                    matched_terms.append((term_type, t))

    # 统计：按术语去重，保留出现频次
    from collections import Counter
    term_freq = Counter()
    for tt, t in matched_terms:
        term_freq[(tt, t)] += 1

    # 过滤：长度 2-60，非停用词，不与现有 PWS 重复
    unique_terms = {}  # (term_type, term_text) -> count
    for (tt, t), count in term_freq.items():
        if len(t) < 2 or len(t) > 60:
            filter_stats["length"] += 1
            continue
        if t.lower() in STOPWORDS:
            filter_stats["stopword"] += 1
            continue
        # 检查是否与现有 PWS 库重复
        if t.lower() in existing_terms:
            filter_stats["existing"] += 1
            continue
        unique_terms[(tt, t)] = count

    print(f"\n[extraction] Matched terms (raw): {len(matched_terms)}")
    print(f"Unique valid terms (freq≥1): {len(unique_terms)}")
    print(f"Filtered out: existing={filter_stats['existing']}, stopword={filter_stats['stopword']}, length={filter_stats['length']}")

    # 构建新条目
    supplement_items = []
    new_items = []

    for (tt, t), count in unique_terms.items():
        pws_category, subcategory = classify(t, tt)

        # 检查是否 term_zh 已存在（中文翻译匹配）
        is_supplement = False
        if t.lower() in existing_zh:
            # 找到现有条目的 id
            for f in sorted(glob.glob("keywords/categories/*.json")):
                basename = os.path.basename(f)
                if basename in ("_pending_review.json", "term_zh_supplement.json"):
                    continue
                with open(f) as fh:
                    data = json.load(fh)
                for kw in data:
                    if (kw.get("term_zh") or "").strip().lower() == t.lower():
                        supplement_items.append({
                            "existing_id": kw["id"],
                            "term_zh": t,
                            "occurrence_count": count,
                        })
                        is_supplement = True
                        break
                if is_supplement:
                    break

        if not is_supplement:
            kw = {
                "id": make_id(pws_category, t),
                "term": t,
                "term_zh": "",
                "category": pws_category,
                "subcategory": subcategory,
                "weight": 0.6,
                "score": 0.6,
                "source": "BeatAPI/awesome-minimax-h3-prompts",
                "compatibility": ["kling", "runway", "minimax_h3"],
                "is_negative": False,
                "needs_review": True,
                "_term_type": tt,
                "occurrence_count": count,
            }
            new_items.append(kw)

    # 写入 _pending_review.json（追加到现有 shuixian 条目）
    print(f"\n[output] Writing {len(new_items)} new candidates to {PENDING_FILE}")
    existing_pending = []
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE) as f:
            existing_pending = json.load(f)
    merged_pending = existing_pending + new_items
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_pending, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 统计报告
    new_unique = len(new_items)

    print("\n" + "=" * 60)
    print("MINIMAX H3 PROMPTS IMPORT REPORT")
    print("=" * 60)
    print(f"Data files processed: {len(json_files)}")
    print(f"Total entries processed: {len(all_items)}")
    print(f"Raw matched terms: {len(matched_terms)}")
    print(f"Unique valid terms (freq≥1): {len(unique_terms)}")
    print(f"Filtered out: existing={filter_stats['existing']}, stopword={filter_stats['stopword']}, length={filter_stats['length']}")
    print(f"Matched to existing PWS term_zh: {len(supplement_items)}")
    print(f"New candidates (needs_review): {new_unique}")

    # 检查产出规模
    if 100 <= new_unique <= 500:
        print(f"\n✓ Within target range (100-500)")
    elif new_unique > 500:
        print(f"\n⚠️ Above max 500 ({new_unique} candidates)")
    else:
        print(f"\n⚠️ Below min 100 (only {new_unique})")

    # 按类型分布
    print("\nType distribution (new candidates):")
    type_dist = {}
    for kw in new_items:
        tt = kw.get("_term_type", "unknown")
        type_dist[tt] = type_dist.get(tt, 0) + 1
    for tt in sorted(type_dist.keys()):
        print(f"  {tt:20s}: {type_dist[tt]}")

    # 按分类分布
    print("\nCategory distribution (new candidates):")
    cat_dist = {}
    for kw in new_items:
        c = kw["category"]
        cat_dist[c] = cat_dist.get(c, 0) + 1
    for cat in sorted(cat_dist.keys()):
        print(f"  {cat:20s}: {cat_dist[cat]}")

    # Top 30 terms by frequency
    print(f"\nTop 30 terms by frequency:")
    for (tt, t), count in sorted(unique_terms.items(), key=lambda x: -x[1])[:30]:
        print(f"  {t}: {count} (type={tt})")

    print(f"\nOutput file: {PENDING_FILE} ({len(new_items)} new candidates)")
    print("=" * 60)


if __name__ == "__main__":
    main()
