#!/usr/bin/env python3
"""
pws-stats — Prompt Warehouse 统计工具

生成关键词和模板的覆盖率统计报告。

Usage:
  python3 tools/pws-stats.py
  python3 tools/pws-stats.py --detailed
  python3 tools/pws-stats.py --category quality
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

def load_all_keywords():
    all_kws = []
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        data = json.load(open(fp))
        for item in (data if isinstance(data, list) else [data]):
            item["_source_file"] = fp
            all_kws.append(item)
    return all_kws

def load_all_templates():
    all_templates = []
    for fp in sorted(glob.glob("templates/*.json")):
        if "_meta" in fp or "_legacy" in fp:
            continue
        data = json.load(open(fp))
        if isinstance(data, list):
            all_templates.extend(data)
        elif isinstance(data, dict) and "variants" in data:
            all_templates.append(data)
    return all_templates

def keyword_stats(kws, detailed=False):
    total = len(kws)
    if total == 0:
        print("No keywords found.")
        return

    # Required field coverage
    fields = {
        "id": lambda x: bool(x.get("id")),
        "term": lambda x: bool(x.get("term")),
        "term_zh": lambda x: bool(x.get("term_zh")),
        "category": lambda x: bool(x.get("category")),
        "subcategory": lambda x: bool(x.get("subcategory")),
        "aliases": lambda x: bool(x.get("aliases")),
        "aliases_zh": lambda x: bool(x.get("aliases_zh")),
        "labels": lambda x: bool(x.get("labels")),
        "labels_zh": lambda x: bool(x.get("labels_zh")),
        "score": lambda x: x.get("score") is not None,
        "priority": lambda x: bool(x.get("priority")),
        "lifecycle": lambda x: bool(x.get("lifecycle")),
        "tags": lambda x: bool(x.get("tags")),
        "created_at": lambda x: bool(x.get("created_at")),
        "updated_at": lambda x: bool(x.get("updated_at")),
        "source": lambda x: bool(x.get("source")),
    }

    print("=" * 60)
    print("  PWS Keyword Statistics")
    print("=" * 60)
    print(f"\n📊 Total keywords: {total}")

    print(f"\n📝 Required field coverage:")
    for field, check in fields.items():
        if field in ("id", "term", "category", "subcategory"):
            continue  # already required by schema
        count = sum(1 for kw in kws if check(kw))
        pct = count / total * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {field:<15s} {count:>5d}/{total} ({pct:5.1f}%) {bar}")

    print(f"\n🌍 Bilingual coverage:")
    zh_only = sum(1 for kw in kws if kw.get("term_zh") and not kw.get("term"))
    en_only = sum(1 for kw in kws if kw.get("term") and not kw.get("term_zh"))
    both = sum(1 for kw in kws if kw.get("term") and kw.get("term_zh"))
    neither = sum(1 for kw in kws if not kw.get("term") and not kw.get("term_zh"))
    print(f"  Both en + zh: {both} ({both/total*100:.1f}%)")
    print(f"  EN only:      {en_only} ({en_only/total*100:.1f}%)")
    print(f"  ZH only:      {zh_only} ({zh_only/total*100:.1f}%)")
    print(f"  Neither:      {neither} ({neither/total*100:.1f}%)")

    print(f"\n📈 Score distribution:")
    score_bins = defaultdict(int)
    for kw in kws:
        s = kw.get("score", 0)
        if s is None:
            score_bins["null"] += 1
        elif s >= 0.9:
            score_bins["0.9-1.0"] += 1
        elif s >= 0.75:
            score_bins["0.75-0.9"] += 1
        elif s >= 0.5:
            score_bins["0.5-0.75"] += 1
        else:
            score_bins["<0.5"] += 1
    for bin_name in ["0.9-1.0", "0.75-0.9", "0.5-0.75", "<0.5", "null"]:
        if bin_name in score_bins:
            print(f"  {bin_name:<12s} {score_bins[bin_name]:>5d}")

    print(f"\n🔄 Lifecycle distribution:")
    life_counts = Counter(kw.get("lifecycle", "unknown") for kw in kws)
    for lc, count in life_counts.most_common():
        print(f"  {lc:<12s} {count:>5d} ({count/total*100:.1f}%)")

    print(f"\n📁 Category breakdown:")
    cat_counts = Counter(kw.get("category", "unknown") for kw in kws)
    for cat, count in cat_counts.most_common():
        print(f"  {cat:<18s} {count:>5d}")

    if detailed:
        print(f"\n📋 Subcategory breakdown:")
        sub_counts = Counter(
            f"{kw.get('category','?')}/{kw.get('subcategory','?')}" for kw in kws
        )
        for sub, count in sub_counts.most_common():
            print(f"  {sub:<35s} {count:>5d}")

    # Print coverage tip
    zh_pct = both / total * 100 if total > 0 else 0
    print(f"\n💡 term_zh coverage: {zh_pct:.1f}%")
    if zh_pct < 20:
        print("   Run: python3 tools/pws-translate.py --translate-all")
    elif zh_pct < 50:
        print("   Recommend: manual review of remaining untranslated keywords")

    # Translation index stats
    idx_path = os.path.join("keywords", "_translations.jsonl")
    if os.path.exists(idx_path):
        entries = [json.loads(line) for line in open(idx_path) if line.strip()]
        print(f"\n📖 Translation index: {len(entries)} entries")

def template_stats(templates):
    if not templates:
        print("No templates found.")
        return
    print(f"\n{'=' * 60}")
    print("  PWS Template Statistics")
    print(f"{'=' * 60}")
    total = len(templates)
    print(f"\n📊 Total templates: {total}")

    zh_names = sum(1 for t in templates if t.get("name_zh"))
    zh_desc = sum(1 for t in templates if t.get("description_zh"))
    variants_total = sum(len(t.get("variants", [])) for t in templates)
    variants_zh = sum(
        1
        for t in templates
        for v in t.get("variants", [])
        if v.get("description_zh")
    )

    print(f"  name_zh:       {zh_names}/{total} ({zh_names/total*100:.1f}%)")
    print(f"  description_zh:{zh_desc}/{total} ({zh_desc/total*100:.1f}%)")
    print(f"  Variants:      {variants_total} total, {variants_zh} with zh descriptions")

def main():
    parser = argparse.ArgumentParser(description="PWS Statistics Tool")
    parser.add_argument("--detailed", action="store_true", help="Show subcategory breakdown")
    parser.add_argument("--category", metavar="CAT", help="Show stats for one category only")
    args = parser.parse_args()

    kws = load_all_keywords()
    if args.category:
        kws = [kw for kw in kws if kw.get("category") == args.category]

    keyword_stats(kws, detailed=args.detailed)

    templates = load_all_templates()
    template_stats(templates)

if __name__ == "__main__":
    main()
