#!/usr/bin/env python3
"""
pws-merge-categories — Category Consolidation Tool

合并 keywords/categories/ 下的冗余分类文件，实现精简计划
（参见 docs/CATEGORY_CONSOLIDATION.md）。

执行模式：
  --dry-run    只输出将要做的事情，不修改文件（默认）
  --apply      实际执行合并（先备份到 .bak）
  --rollback   从 .bak 恢复所有文件

Usage:
  python3 tools/pws-merge-categories.py --dry-run
  python3 tools/pws-merge-categories.py --apply
  python3 tools/pws-merge-categories.py --rollback
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

CATEGORIES_DIR = "keywords/categories"
BACKUP_DIR = "keywords/categories/.bak-consolidation"

# 合并映射表：(source_file, source_subcategory) -> (target_file, target_subcategory)
# target_subcategory 为 None 表示保留原 subcategory
# exclude_subcats: 在源文件中要排除的 subcategory（不导入）
MERGE_PLAN = {
    # 1. style.json 整体合并到 styles.json
    "style.json": {
        "target": "styles.json",
        "map": {"(ALL)": "art"},  # 所有 subcategory 改为 art
    },
    # 2. aesthetic.json: mainstream + niche -> aesthetic; 剔除 era/mood
    "aesthetic.json": {
        "target": "styles.json",
        "map": {"mainstream": "aesthetic", "niche": "aesthetic"},
        "exclude": ["era", "mood"],  # era 重复到 era.json，mood 重复到 character.json
    },
    # 3. atmosphere.json -> lighting.json
    "atmosphere.json": {
        "target": "lighting.json",
        "map": {"(ALL)": "atmosphere"},
    },
    # 4. mood.json -> character.json
    "mood.json": {
        "target": "character.json",
        "map": {"(ALL)": "mood"},
    },
    # 5. pose.json -> character.json
    "pose.json": {
        "target": "character.json",
        "map": {"(ALL)": "pose"},
    },
    # 6. wardrobe.json -> clothing.json
    "wardrobe.json": {
        "target": "clothing.json",
        "map": {
            "archetype": "wardrobe-archetype",
            "top": "wardrobe-top",
            "bottom": "wardrobe-bottom",
            "outerwear": "wardrobe-outerwear",
            "footwear": "wardrobe-footwear",
            "headwear": "wardrobe-headwear",
            "accessories": "wardrobe-accessories",
            "color-palette": "wardrobe-color-palette",
            "material": "wardrobe-material",
            "era": "wardrobe-era",
        },
    },
    # 7. setting.json -> scene.json
    "setting.json": {
        "target": "scene.json",
        "map": {
            "indoor": "indoor",
            "urban": "urban",
            "nature": "nature",
            "fantastical": "fantastical",
        },
    },
    # 8. backdrop.json -> scene.json
    "backdrop.json": {
        "target": "scene.json",
        "map": {"(ALL)": "backdrop"},
    },
    # 9. lens.json -> composition.json（剔除 term 重复的词）
    "lens.json": {
        "target": "composition.json",
        "map": {"(ALL)": "lens"},
        "exclude_terms": ["anamorphic lens", "fisheye lens"],  # composition.json/lens 已有
    },
    # 10. camera-format.json -> composition.json
    "camera-format.json": {
        "target": "composition.json",
        "map": {"(ALL)": "camera-format"},
    },
    # 11. camera-motions.json -> composition.json
    "camera-motions.json": {
        "target": "composition.json",
        "map": {"(ALL)": "camera-motions"},
    },
    # 12. photo-genre.json -> photographer.json
    "photo-genre.json": {
        "target": "photographer.json",
        "map": {"(ALL)": "genre"},
    },
    # 13. post-process.json -> color-look.json
    "post-process.json": {
        "target": "color-look.json",
        "map": {"(ALL)": "post-process"},
    },
}


# ---------- helpers ----------

def load_json(path):
    """Load JSON file, exit with error on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        print(f"❌ Cannot read {path}: {e}")
        sys.exit(1)


def write_json(path, data):
    """Write JSON file, exit with error on failure."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Cannot write {path}: {e}")
        sys.exit(1)


def slugify(text):
    """Convert text to id-safe slug."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:40]  # limit length


def build_new_id(target_cat, target_sub, term, existing_ids):
    """Build id in {category}_{subcategory}_{slug} format, ensure uniqueness."""
    slug = slugify(term)
    if not slug:
        slug = "kw"
    base = f"{target_cat}_{target_sub}_{slug}"
    candidate = base
    n = 2
    while candidate in existing_ids:
        candidate = f"{base}_{n}"
        n += 1
    return candidate


# ---------- core ----------

def collect_existing_ids():
    """Collect all existing IDs across all category files."""
    ids = set()
    for fp in sorted(glob.glob(f"{CATEGORIES_DIR}/*.json")):
        try:
            data = load_json(fp)
        except Exception as e:
            print(f"WARN: failed to load {fp}: {e}", file=sys.stderr)
            continue
        for item in (data if isinstance(data, list) else [data]):
            iid = item.get("id")
            if iid:
                ids.add(iid)
    return ids


def remap_item(item, target_cat, target_sub, existing_ids):
    """Remap a single keyword item to target category/subcategory, with new ID."""
    new_item = dict(item)
    new_item["category"] = target_cat
    new_item["subcategory"] = target_sub

    # Update timestamp
    new_item["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Rebuild id
    new_id = build_new_id(target_cat, target_sub, new_item.get("term", ""), existing_ids)
    new_item["id"] = new_id
    existing_ids.add(new_id)

    return new_item


def plan_merges(verbose=True):
    """Plan all merges, return list of operations."""
    existing_ids = collect_existing_ids()
    operations = []  # (source_file, target_file, items_to_move)

    for source_file, plan in MERGE_PLAN.items():
        source_path = f"{CATEGORIES_DIR}/{source_file}"
        if not os.path.exists(source_path):
            print(f"WARN: source file not found: {source_path}", file=sys.stderr)
            continue

        data = load_json(source_path)
        if not isinstance(data, list):
            data = [data]

        target_file = plan["target"]
        target_cat = target_file.replace(".json", "")
        mapping = plan["map"]
        exclude_subs = set(plan.get("exclude", []))
        exclude_ids = set(plan.get("exclude_ids", []))

        moved = []
        skipped = []

        for item in data:
            old_sub = item.get("subcategory", "")
            item_id = item.get("id", "")
            item_term = (item.get("term") or "").strip().lower()
            exclude_terms = set(t.lower() for t in plan.get("exclude_terms", []))

            # Skip excluded subcategories
            if old_sub in exclude_subs:
                skipped.append({"id": item_id, "term": item.get("term"), "reason": f"subcategory '{old_sub}' excluded"})
                continue

            # Skip excluded ids
            if item_id in exclude_ids:
                skipped.append({"id": item_id, "term": item.get("term"), "reason": f"id '{item_id}' excluded"})
                continue

            # Skip excluded terms
            if item_term in exclude_terms:
                skipped.append({"id": item_id, "term": item.get("term"), "reason": f"term '{item_term}' already exists in target"})
                continue

            # Determine target subcategory
            if "(ALL)" in mapping:
                new_sub = mapping["(ALL)"]
            else:
                new_sub = mapping.get(old_sub, old_sub)

            new_item = remap_item(item, target_cat, new_sub, existing_ids)
            moved.append({
                "source": f"{source_file}/{old_sub}",
                "target": f"{target_file}/{new_sub}",
                "old_id": item_id,
                "new_id": new_item["id"],
                "term": item.get("term"),
            })

        operations.append({
            "source_file": source_file,
            "target_file": target_file,
            "moved": moved,
            "skipped": skipped,
        })

    return operations, existing_ids


def print_plan(operations):
    print("=" * 78)
    print("  PWS Category Consolidation Plan")
    print("=" * 78)

    total_moved = 0
    total_skipped = 0

    for op in operations:
        print(f"\n📦 {op['source_file']}  →  {op['target_file']}")
        print(f"   Move {len(op['moved'])} keywords, skip {len(op['skipped'])}")
        total_moved += len(op["moved"])
        total_skipped += len(op["skipped"])

        if op["moved"]:
            for m in op["moved"][:3]:
                print(f"     • {m['source']} → {m['target']}: {m['term']!r}")
            if len(op["moved"]) > 3:
                print(f"     ... and {len(op['moved']) - 3} more")

        if op["skipped"]:
            for s in op["skipped"]:
                print(f"     ⛔ SKIP {s['id']} ({s['term']!r}): {s['reason']}")

    print(f"\n{'=' * 78}")
    print(f"  Total: {total_moved} keywords will be moved, {total_skipped} skipped")
    print(f"  Source files: {len(operations)} (will be deleted after merge)")
    print("=" * 78)


def apply_merges(operations):
    """Apply the merge plan: write to target files, delete source files."""
    # Step 1: backup
    import shutil as _shutil
    import sys as _sys
    from contextlib import suppress
    _shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    try:
        os.makedirs(BACKUP_DIR)
    except OSError as e:
        print(f"❌ Cannot create backup dir {BACKUP_DIR}: {e}")
        sys.exit(1)

    for fp in sorted(glob.glob(f"{CATEGORIES_DIR}/*.json")):
        shutil.copy2(fp, BACKUP_DIR)
    print(f"📦 Backup created at {BACKUP_DIR}")

    targets = {}
    for op in operations:
        target_path = f"{CATEGORIES_DIR}/{op['target_file']}"
        if target_path not in targets:
            targets[target_path] = load_json(target_path)
            if not isinstance(targets[target_path], list):
                targets[target_path] = [targets[target_path]]

    # Step 3: append merged items
    added_count = 0
    for op in operations:
        source_path = f"{CATEGORIES_DIR}/{op['source_file']}"
        target_path = f"{CATEGORIES_DIR}/{op['target_file']}"
        source_data = load_json(source_path)
        if not isinstance(source_data, list):
            source_data = [source_data]

        exclude_subs = set(MERGE_PLAN[op["source_file"]].get("exclude", []))
        exclude_ids = set(MERGE_PLAN[op["source_file"]].get("exclude_ids", []))
        mapping = MERGE_PLAN[op["source_file"]]["map"]
        target_cat = op["target_file"].replace(".json", "")

        # Reuse existing_ids computation
        existing_ids = {item.get("id") for item in targets[target_path] if item.get("id")}

        for item in source_data:
            old_sub = item.get("subcategory", "")
            item_id = item.get("id", "")
            item_term = (item.get("term") or "").strip().lower()
            exclude_terms = set(t.lower() for t in MERGE_PLAN[op["source_file"]].get("exclude_terms", []))

            if old_sub in exclude_subs or item_id in exclude_ids:
                continue
            if item_term in exclude_terms:
                continue

            new_sub = mapping["(ALL)"] if "(ALL)" in mapping else mapping.get(old_sub, old_sub)
            new_item = remap_item(item, target_cat, new_sub, existing_ids)
            targets[target_path].append(new_item)
            added_count += 1

    # Step 4: write target files
    for target_path, items in targets.items():
        write_json(target_path, items)
        print(f"  ✓ Wrote {target_path} ({len(items)} keywords)")

    # Step 5: delete source files
    deleted = []
    for op in operations:
        source_path = f"{CATEGORIES_DIR}/{op['source_file']}"
        if os.path.exists(source_path):
            try:
                os.remove(source_path)
            except OSError as e:
                print(f"❌ Cannot delete {source_path}: {e}")
                sys.exit(1)
            deleted.append(op["source_file"])
            print(f"  🗑  Deleted {source_path}")

    print(f"\n✅ Consolidation applied: {added_count} keywords moved, {len(deleted)} source files removed")
    print(f"   Backup kept at: {BACKUP_DIR}")
    return added_count, len(deleted)


def rollback():
    """Restore from backup."""
    import shutil as _shutil
    _shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    if not os.path.exists(BACKUP_DIR):
        print("❌ No backup found at", BACKUP_DIR)
        return

    restored = 0
    for fp in sorted(glob.glob(f"{BACKUP_DIR}/*.json")):
        target = f"{CATEGORIES_DIR}/{os.path.basename(fp)}"
        shutil.copy2(fp, target)
        restored += 1
        print(f"  ✓ Restored {target}")

    _shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    print(f"\n✅ Rolled back {restored} files. Backup directory removed.")


def main():
    parser = argparse.ArgumentParser(description="PWS Category Consolidation Tool")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Show plan without applying (default)")
    parser.add_argument("--apply", action="store_true", help="Apply the consolidation")
    parser.add_argument("--rollback", action="store_true", help="Rollback from backup")
    args = parser.parse_args()

    if args.rollback:
        rollback()
        return

    operations, _ = plan_merges(verbose=True)
    print_plan(operations)

    if args.apply:
        print("\n⚠️  APPLYING CONSOLIDATION...")
        confirm = input("Type 'yes' to continue, anything else to abort: ")
        if confirm.strip().lower() == "yes":
            apply_merges(operations)
        else:
            print("Aborted.")
    else:
        print("\n💡 This was a dry run. Use --apply to execute.")


if __name__ == "__main__":
    main()
