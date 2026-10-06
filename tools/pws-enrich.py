#!/usr/bin/env python3
"""
pws-enrich.py — Enrich existing PWS keywords with missing fields.

What it does:
    1. Fill missing `created_at` / `updated_at` timestamps
    2. Re-grade `priority` based on quality signals in `notes`/`term`
    3. Generate `aliases` for high-value terms (high score, quality category)
    4. Generate `aliases_zh` for keywords that have term_zh

Usage:
    python3 tools/pws-enrich.py [--apply] [--dry-run]
"""

import json
import os
import sys
from datetime import datetime, timezone


# ---------- high-value keyword patterns ----------

# Keywords that are almost universally "high" priority in AI generation
HIGH_VALUE_TERMS = {
    # Quality boosters (nearly always high)
    "masterpiece", "best quality", "ultra-detailed", "high resolution", "8k resolution",
    "ultra highres", "intricate details", "sharp focus", "award-winning",
    "photorealistic", "cinematic", "gorgeous", "stunning",
    "professional", "refined", "subtle", "beautiful", "exquisite",
    "beautiful lighting", "perfect composition", "perfectly balanced",
    # Composition
    "golden ratio", "centered composition",
    # Character core
    "hero shot", "eye contact", "three-quarter view", "full body",
    "detailed face", "detailed hands",
}

# Terms that are typically "low" priority (niche, experimental, or optional)
LOW_VALUE_TERMS = {
    "color blend", "color model", "color palette", "color wheel",
    "colorized", "coloroid", "complimentary colors", "contrast",
    "cool color palette", "warm color palette", "analogous colors",
    "chroma", "chromatopsia", "chloropsia", "cmyk",
    "agfacolor", "autochrome", "cinecolor",
}

# Map of high-value terms → (aliases_en, aliases_zh)
# Pairs of common synonyms that AI generators recognize
HIGH_VALUE_ALIASES = {
    "masterpiece": (["best work", "top tier", "excellent work"], ["杰作", "最好作品", "顶级"]),
    "best quality": (["max quality", "highest quality", "top quality"], ["最高质量", "顶级质量"]),
    "ultra-detailed": (["highly detailed", "intricate", "extremely detailed"], ["超精细", "复杂细节", "高度细节"]),
    "high resolution": (["hd", "high res", "sharp"], ["高分辨率", "高清"]),
    "8k resolution": (["8k", "ultra hd", "4k"], ["8k分辨率", "超高清"]),
    "cinematic": (["movie-like", "film-like", "cinematic look"], ["电影感", "电影风格"]),
    "photorealistic": (["photo-realistic", "realistic", "photo-real"], ["照片级真实", "写实", "照片真实"]),
    "graceful lighting": (["elegant lighting", "refined lighting"], ["优雅的灯光", "精致的灯光"]),
    "golden hour": (["golden time", "sunset glow", "warm sunset"], ["黄金时段", "日落光芒", "温暖日落"]),
    "dramatic lighting": (["strong lighting", "intense lighting", "bold lighting"], ["戏剧性灯光", "强烈灯光"]),
    "studio lighting": (["even lighting", "professional lighting", "clean lighting"], ["工作室灯光", "均匀灯光", "专业灯光"]),
    "key light": (["main light", "primary light"], ["主光", "主要光源"]),
    "rim light": (["back light", "edge light", "hair light"], ["轮廓光", "边缘光", "发丝光"]),
    "volumetric lighting": (["light rays", "god rays", "light beams", "light shafts"], ["体积光", "光柱", "丁达尔效应"]),
    "bokeh": (["background blur", "depth of field", "out of focus background", "blurry background"], ["散景", "背景虚化", "景深效果"]),
    "rule of thirds": (["golden ratio", "composition rule", "balanced composition"], ["三分法", "黄金分割", "构图规则"]),
    "close-up": (["closeup", "proximity shot", "detail shot", "magnified view"], ["特写", "近景", "特写镜头"]),
    "medium shot": (["mid shot", "waist-up shot", "torso shot"], ["中景", "腰部以上镜头"]),
    "wide shot": (["long shot", "full shot", "panoramic view"], ["远景", "全景", "广角镜头"]),
    "hero shot": (["imposing shot", "powerful shot", "dramatic angle"], ["英雄镜头", "力量感镜头", "戏剧性角度"]),
    "eye contact": (["looking at viewer", "looking at camera", "direct gaze"], ["眼神接触", "看向观众", "直视镜头"]),
}

# Category → subcategory hint for generating aliases_zh from category/subcategory
CATEGORY_ZH_HINTS = {
    "quality": "质量", "composition": "构图", "lighting": "灯光",
    "character": "角色", "clothing": "服装", "styles": "风格",
    "negative": "负面", "scene": "场景", "panel": "分镜",
    "action-fx": "动作特效", "character-fx": "角色特效", "color-look": "色彩分级",
    "era": "时代", "framing": "景别", "held-prop": "手持道具",
    "material": "材质", "photographer": "摄影师", "render-quality": "渲染",
    "temporal": "时间", "transitions": "转场",
}


def _cat_files():
    return sorted(__import__('glob').glob("keywords/categories/*.json"))


def load_keywords_by_file() -> tuple[list, dict]:
    """Load all keywords, mapping by filename."""
    all_items = []
    by_file = {}
    for fp in _cat_files():
        try:
            with open(fp, "rb") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            by_file[fp] = data
            all_items.extend(data)
        else:
            by_file[fp] = [data]
            all_items.append(data)
    return all_items, by_file


def is_high_value(term: str) -> bool:
    """Check if a term is in the high-value set."""
    t = term.lower().strip()
    return t in HIGH_VALUE_TERMS


def is_low_value(term: str) -> bool:
    """Check if a term is in the low-value set."""
    t = term.lower().strip()
    return t in LOW_VALUE_TERMS


def get_aliases_for_term(term: str) -> tuple[list, list]:
    """Return (aliases_en, aliases_zh) for a known high-value term."""
    t = term.lower().strip()
    if t in HIGH_VALUE_ALIASES:
        return HIGH_VALUE_ALIASES[t]
    return [], []


def grade_priority(item: dict) -> str:
    """Determine optimal priority based on term, score, and category."""
    term = (item.get("term", "") or "").lower().strip()
    score = item.get("score", 0.5)
    cat = item.get("category", "")

    # If already explicitly set (not default "medium"), leave it
    if item.get("priority") and item["priority"] != "medium":
        return item["priority"]

    # High-value terms get high priority
    if is_high_value(term):
        return "high"

    # Explicit high score → high priority
    if score is not None and score >= 0.90:
        return "high"

    # Score 0.75-0.89 with quality-related category → high
    if score is not None and 0.75 <= score < 0.90 and cat in ("quality", "negative"):
        return "high"

    # Low-value terms (color models, etc.) → low
    if is_low_value(term):
        return "low"

    # Default → medium
    return "medium"


def generate_aliases_if_missing(item: dict) -> dict:
    """Add aliases/en and aliases_zh for high-value terms that lack them."""
    term = (item.get("term", "") or "").strip()
    aliases_en, aliases_zh = get_aliases_for_term(term)

    if aliases_en and not item.get("aliases"):
        item["aliases"] = aliases_en
    if aliases_zh and not item.get("aliases_zh"):
        item["aliases_zh"] = aliases_zh

    return item


def enrich_keywords(items: list) -> dict:
    """Enrich a batch of keywords, return summary counts."""
    summary = {
        "total": len(items),
        "created_at_filled": 0,
        "updated_at_filled": 0,
        "priority_changed": 0,
        "aliases_added": 0,
        "aliases_zh_added": 0,
        "timestamps_set": 0,
    }
    now = datetime.now(timezone.utc).isoformat()

    for item in items:
        modified = False

        # 1. Fill timestamps
        if not item.get("created_at"):
            source = item.get("source", "")
            if "MidJourney" in source:
                item["created_at"] = "2026-09-28T00:00:00+00:00"
            elif "nodaro" in source.lower() or "danbooru" in source.lower() or "civitai" in source.lower():
                item["created_at"] = "2026-09-29T00:00:00+00:00"
            elif "h3" in source.lower():
                item["created_at"] = "2026-09-28T00:00:00+00:00"
            else:
                item["created_at"] = "2026-09-28T00:00:00+00:00"
            summary["created_at_filled"] += 1
            modified = True

        if not item.get("updated_at"):
            item["updated_at"] = now
            summary["updated_at_filled"] += 1
            summary["timestamps_set"] += 1
            modified = True

        # 2. Re-grade priority
        new_pri = grade_priority(item)
        if item.get("priority") != new_pri:
            item["priority"] = new_pri
            summary["priority_changed"] += 1
            modified = True

        # 3. Add aliases for high-value terms
        item = generate_aliases_if_missing(item)
        if item.get("aliases") and not item.get("_aliases_orig"):
            summary["aliases_added"] += 1
            modified = True
        if item.get("aliases_zh") and not item.get("_aliases_zh_orig"):
            summary["aliases_zh_added"] += 1
            modified = True

        if modified:
            item["_enriched_at"] = now

    return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich PWS keywords with missing fields")
    parser.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run)")
    parser.add_argument("--category", help="Only process a specific category file")
    parser.add_argument("--verbose", action="store_true", help="Show per-keyword changes")
    args = parser.parse_args()

    print("🔍 Running PWS enrichment...")
    all_items, by_file = load_keywords_by_file()

    # Filter by category if specified
    if args.category:
        cat_file = f"keywords/categories/{args.category}.json"
        if not os.path.exists(cat_file):
            print(f"❌ Category '{args.category}' not found.")
            sys.exit(1)
        by_file = {cat_file: load_category(cat_file)}
        all_items = by_file[cat_file]

    total_before = len(all_items)

    # Count what needs fixing
    need_created = sum(1 for i in all_items if not i.get("created_at"))
    need_updated = sum(1 for i in all_items if not i.get("updated_at"))
    need_priority = sum(1 for i in all_items if grade_priority(i) != i.get("priority", "medium"))
    need_aliases = sum(1 for i in all_items if not i.get("aliases") and is_high_value(i.get("term", "")))
    need_aliases_zh = sum(1 for i in all_items if not i.get("aliases_zh") and i.get("term_zh") and is_high_value(i.get("term", "")))

    print(f"\n  Total keywords: {total_before}")
    print(f"  Missing created_at: {need_created}")
    print(f"  Missing updated_at: {need_updated}")
    print(f"  Priority re-grading needed: {need_priority}")
    print(f"  Missing aliases (high-value): {need_aliases}")
    print(f"  Missing aliases_zh (high-value, has term_zh): {need_aliases_zh}")

    # Run enrichment
    if args.category:
        cat_file = f"keywords/categories/{args.category}.json"
        result_by_file = {cat_file: load_category(cat_file)}
    else:
        result_items, result_by_file = load_keywords_by_file()

    all_summaries = {}
    for cat_file, items in result_by_file.items():
        summary = enrich_keywords(items)
        summary["file"] = cat_file
        all_summaries[cat_file] = summary

        if args.verbose:
            changes = [i for i in items if i.get("_enriched_at")]
            if changes:
                print(f"\n  Changes in {cat_file} ({len(changes)} keywords):")
                for c in changes[:10]:
                    print(f"    {c.get('id')}: pri={c.get('priority')} aliases={'✓' if c.get('aliases') else '✗'} tz={'✓' if c.get('aliases_zh') else '✗'}")
                if len(changes) > 10:
                    print(f"    ... and {len(changes)-10} more")

    print(f"\n{'=' * 60}")
    print("  SUMMARY (dry-run)")
    print(f"{'=' * 60}")
    for cat_file, s in all_summaries.items():
        cat = cat_file.split("/")[-1].replace(".json", "")
        print(f"  {cat:15s} created_at={s['created_at_filled']:>4} updated_at={s['updated_at_filled']:>4} priority={s['priority_changed']:>4} aliases={s['aliases_added']:>4} aliases_zh={s['aliases_zh_added']:>4}")
    grand = {k: sum(s[k] for s in all_summaries.values()) for k in all_summaries[next(iter(all_summaries))]}
    print(f"\n  TOTAL: created_at={grand['created_at_filled']:>4} updated_at={grand['updated_at_filled']:>4} priority={grand['priority_changed']:>4} aliases={grand['aliases_added']:>4} aliases_zh={grand['aliases_zh_added']:>4}")

    if args.apply:
        # Write changes back
        written = 0
        for cat_file, items in result_by_file.items():
            try:
                with open(cat_file, "wb") as fh:
                    payload = json.dumps(items, ensure_ascii=False, indent=2).encode("utf-8")
                    fh.write(payload)
                    fh.write(b"\n")
                written += 1
            except OSError:
                print(f"  ⚠️  Could not write {cat_file}")
        print(f"\n✅ Changes written to {written} category file(s)")
        print("  (Use `git diff` to review changes)")
    else:
        print("\n  Run with --apply to write changes.")


def load_category(cat_file):
    try:
        with open(cat_file, "rb") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return data
    return [data]


if __name__ == "__main__":
    main()
