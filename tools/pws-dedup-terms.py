#!/usr/bin/env python3
"""
pws-dedup-terms (conservative) — Remove only TRUE duplicates:
same term AND same category/subcategory.

Cross-category duplicates (e.g. 'looking up' in character/eyes AND
composition/angles) are semantically distinct and KEPT.

Usage:
  python3 tools/pws-dedup-terms.py --dry-run   # default
  python3 tools/pws-dedup-terms.py --apply
  python3 tools/pws-dedup-terms.py --rollback
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone

CATEGORIES_DIR = "keywords/categories"
BACKUP_DIR = "keywords/categories/.bak-dedup-terms"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    if args.rollback:
        if not os.path.exists(BACKUP_DIR):
            print("No backup at", BACKUP_DIR)
            return
        for fp in sorted(glob.glob(f"{BACKUP_DIR}/*.json")):
            target = f"{CATEGORIES_DIR}/{os.path.basename(fp)}"
            shutil.copy2(fp, target)
        shutil.rmtree(BACKUP_DIR)
        n = len(glob.glob(f"{BACKUP_DIR}/*.json"))
        print(f"✅ Restored from {BACKUP_DIR}")
        return

    # Group by (term, category, subcategory) — only true duplicates
    by_key = defaultdict(list)
    for fp in sorted(glob.glob(f"{CATEGORIES_DIR}/*.json")):
        with open(fp) as f:
            data = json.load(f)
        for idx, item in enumerate(data):
            term = (item.get("term") or "").strip()
            cat = item.get("category")
            sub = item.get("subcategory")
            if term:
                by_key[(term, cat, sub)].append({
                    "file": fp,
                    "index": idx,
                    "id": item.get("id"),
                    "score": item.get("score", 0.5) or 0.5,
                    "source": item.get("source"),
                    "term": term,
                    "cat": cat,
                    "sub": sub,
                })

    true_dupes = {k: kws for k, kws in by_key.items() if len(kws) > 1}

    if not true_dupes:
        print("✅ No true duplicates (same term + same category/subcategory).")
        return

    removal_plan = []
    for (term, cat, sub), kws in true_dupes.items():
        kws_sorted = sorted(
            kws,
            key=lambda k: (
                -k["score"],                         # highest score first
                0 if "nodaro-prompts" in (k.get("source") or "") else 1,  # prefer nodaro
                0 if "mj" in (k.get("source") or "").lower() else 1,       # then MJ
                len(k["id"] or ""),                  # shorter id first
                k["file"],                           # file order
            ),
        )
        keeper = kws_sorted[0]
        for k in kws_sorted[1:]:
            removal_plan.append({
                "file": k["file"],
                "index": k["index"],
                "id": k["id"],
                "term": term,
                "cat": cat,
                "sub": sub,
                "kept_id": keeper["id"],
                "kept_score": keeper["score"],
                "kept_file": keeper["file"],
                "score_diff": round(keeper["score"] - k["score"], 3),
            })

    print("=" * 78)
    print("  PWS True-Duplicate Term Cleanup")
    print("=" * 78)
    print(f"  Strategy: Keep highest-score instance per (term, category, subcategory)")
    print(f"  Cross-category duplicates are KEPT (semantically distinct)")
    print()
    print(f"  True-duplicate groups: {len(true_dupes)}")
    print(f"  Items to remove: {len(removal_plan)}")
    print()

    by_file = defaultdict(int)
    for r in removal_plan:
        by_file[os.path.basename(r["file"])] += 1
    print("  Removal count per file:")
    for fp, cnt in sorted(by_file.items(), key=lambda x: -x[1]):
        print(f"    {fp}: {cnt}")
    print()

    print("=" * 78)
    print(f"  Sample ({min(40, len(removal_plan))} of {len(removal_plan)})")
    print("=" * 78)
    for r in removal_plan[:40]:
        marker = "🗑 " if r["score_diff"] > 0 else "❓"
        print(f"  {marker} {r['term']!r}  [{r['cat']}/{r['sub']}]")
        print(f"      KEEP   {os.path.basename(r['kept_file'])}: {r['kept_id']} (score={r['kept_score']})")
        print(f"      DROP   {os.path.basename(r['file'])}: {r['id']} (score={r['score_diff']:+.2f} lower)")
    if len(removal_plan) > 40:
        print(f"\n  ... and {len(removal_plan) - 40} more")

    if not args.apply:
        print("\n💡 Dry run. Use --apply to execute.")
        return

    # Apply
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    os.makedirs(BACKUP_DIR)
    for fp in sorted(glob.glob(f"{CATEGORIES_DIR}/*.json")):
        shutil.copy2(fp, BACKUP_DIR)
    print(f"\n📦 Backup at {BACKUP_DIR}")

    by_file = defaultdict(list)
    for r in removal_plan:
        by_file[r["file"]].append(r["index"])

    removed_total = 0
    for fp, indices in by_file.items():
        with open(fp) as f:
            data = json.load(f)
        for idx in sorted(set(indices), reverse=True):
            if idx < len(data):
                data.pop(idx)
                removed_total += 1
        with open(fp, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  ✓ Cleaned {fp}: removed {len(set(indices))} items")

    print(f"\n✅ Removed {removed_total} true-duplicate items.")
    print(f"   Backup at: {BACKUP_DIR}")


if __name__ == "__main__":
    main()
