#!/usr/bin/env python3
"""
pws-add-new.py — Safe keyword ingestion tool for Prompt Warehouse.

Usage:
    # Add keywords from a JSON file (batch)
    python3 tools/pws-add-new.py batch new_keywords.json --category quality --subcategory basic

    # Add a single keyword
    python3 tools/pws-add-new.py single \
        --term "cinematic lighting" --term_zh "电影灯光" \
        --category lighting --subcategory dramatic

    # Dry-run (preview only, no writes)
    python3 tools/pws-add-new.py batch new_keywords.json --category quality --subcategory basic --dry-run

    # Generate a template for the next batch
    python3 tools/pws-add-new.py template --output batch_template.json

The tool:
    1. Loads existing keywords from the target category file
    2. Checks for ID conflicts, term conflicts (cross-category OK), and similar terms
    3. Merges new keywords into the correct category file
    4. Updates keywords/_meta.json (total_keywords, updated_at)
    5. Regenerates data/pws_index.json (flat searchable index)
    6. Writes a changelog entry to CHANGELOG.md
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional

# ---------- constants ----------
KEYWORDS_DIR = "keywords/categories"
META_PATH = "keywords/_meta.json"
INDEX_PATH = "data/pws_index.json"
CHANGELOG_PATH = "CHANGELOG.md"
SIMILAR_THRESHOLD = 0.85  # Levenshtein similarity ratio to flag

# Required fields for a valid keyword entry
REQUIRED_FIELDS = ["id", "term", "category", "subcategory"]
OPTIONAL_EN_FIELDS = ["aliases", "source", "score", "priority", "tags", "notes", "variations"]
OPTIONAL_ZH_FIELDS = ["term_zh", "aliases_zh", "labels_zh"]
METADATA_FIELDS = ["score", "priority", "lifecycle", "usage_count", "success_rate",
                   "created_at", "updated_at", "source", "tags", "notes", "variations",
                   "usage_count", "success_rate"]


def load_category(cat_file: str) -> list:
    """Load a single category file."""
    if not os.path.exists(cat_file):
        return []
    try:
        with open(cat_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {cat_file}: {e}")
        sys.exit(1)
    if isinstance(data, list):
        return data
    return [data]


def load_all_categories() -> dict:
    """Load all category files, returning {filename: [items]}."""
    result = {}
    for fp in sorted(glob.glob(f"{KEYWORDS_DIR}/*.json")):
        result[fp] = load_category(fp)
    return result


def check_id_conflicts(new_items: list, existing_items: list) -> list:
    """Check for exact ID conflicts between new and existing."""
    existing_ids = {i.get("id") for i in existing_items if i.get("id")}
    conflicts = []
    for item in new_items:
        nid = item.get("id", "")
        if nid in existing_ids:
            existing = next((i for i in existing_items if i.get("id") == nid), None)
            conflicts.append({"new_id": nid, "existing": existing, "new_term": item.get("term")})
    return conflicts


def check_term_dupes(new_items: list, all_categories: dict) -> list:
    """Check for exact term+category+subcategory duplicates (cross-category OK)."""
    dupes = []
    for item in new_items:
        term = item.get("term", "").lower().strip()
        cat = item.get("category", "")
        subcat = item.get("subcategory", "")
        for fp, items in all_categories.items():
            for existing in items:
                if (existing.get("category") == cat and
                    existing.get("subcategory") == subcat and
                    existing.get("term", "").lower().strip() == term):
                    dupes.append({
                        "new": item.get("id"),
                        "existing": existing.get("id"),
                        "term": item.get("term"),
                        "category": cat,
                        "subcat": subcat,
                        "new_zh": item.get("term_zh"),
                        "exist_zh": existing.get("term_zh"),
                    })
    return dupes


def check_similar_terms(new_items: list, all_categories: dict, top_n: int = 5) -> list:
    """Find terms with high similarity ratio (potential duplicates)."""
    similar = []
    existing_terms = []
    for fp, items in all_categories.items():
        for item in items:
            existing_terms.append((item.get("term", "").lower().strip(), item.get("id"), fp))

    for item in new_items:
        new_term = item.get("term", "").lower().strip()
        matches = []
        for et, eid, efp in existing_terms:
            ratio = SequenceMatcher(None, new_term, et).ratio()
            if ratio > SIMILAR_THRESHOLD and et != new_term:
                matches.append({"ratio": ratio, "existing_term": et, "existing_id": eid, "file": efp})
        matches.sort(key=lambda x: -x["ratio"])
        if matches:
            similar.append({"new_id": item.get("id"), "new_term": item.get("term"), "matches": matches[:top_n]})
    return similar


def merge_into_category(cat_file: str, new_items: list) -> str:
    """Append new items to a category file, return file path."""
    existing = load_category(cat_file)
    existing.extend(new_items)
    try:
        with open(cat_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write {cat_file}: {e}")
        sys.exit(1)
    return cat_file


def update_meta() -> dict:
    """Update _meta.json: total_keywords and updated_at."""
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {META_PATH}: {e}")
        sys.exit(1)
    try:
        total = 0
        for fp in glob.glob(f"{KEYWORDS_DIR}/*.json"):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    total += len(json.load(f))
            except (json.JSONDecodeError, OSError) as e2:
                print(f"⚠️  Skipped {fp}: {e2}")
    except Exception as e:
        print(f"❌ Failed counting categories: {e}")
        sys.exit(1)
    meta["total_keywords"] = total
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write {META_PATH}: {e}")
        sys.exit(1)
    return meta


def update_index() -> str:
    """Regenerate flat searchable index."""
    # Import and reuse pws-index.py logic
    return _build_index()


def _build_index() -> str:
    """Build flat index from all categories."""
    entries = []
    try:
        for fp in sorted(glob.glob(f"{KEYWORDS_DIR}/*.json")):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    items = json.load(f)
                if isinstance(items, list):
                    for item in items:
                        entry = {
                            "id": item.get("id", ""),
                            "term": item.get("term", ""),
                            "term_zh": item.get("term_zh"),
                            "category": item.get("category", ""),
                            "subcategory": item.get("subcategory", ""),
                            "labels": item.get("labels", []),
                            "labels_zh": item.get("labels_zh", []),
                            "score": item.get("score"),
                            "priority": item.get("priority"),
                            "source": item.get("source"),
                            "tags": item.get("tags", []),
                        }
                        entries.append(entry)
            except (json.JSONDecodeError, OSError) as e:
                print(f"⚠️  Skipped {fp} during index build: {e}")
    except Exception as e:
        print(f"❌ Failed building index: {e}")
        sys.exit(1)
    try:
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0", "total": len(entries), "updated_at": datetime.now(timezone.utc).isoformat(), "entries": entries}, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write index: {e}")
        sys.exit(1)
    return f"{INDEX_PATH}: {len(entries)} entries"


def append_changelog(batch_id: str, added: int, category: str, dry_run: bool = False):
    """Append a new version entry to CHANGELOG.md."""
    version = get_next_version()
    changes = f"Added {added} keyword(s) to {category} via pws-add-new.py (batch: {batch_id})"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to read {CHANGELOG_PATH}: {e}")
        return

    insert_marker = None
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if 'version": "1.8.0"' in line or 'version":  "1.8.0"' in line:
            insert_marker = i

    try:
        if insert_marker:
            new_block = f'''    {{
      "version": "{version}",
      "date": "{now}",
      "changes": [
        "{changes}"
      ],
      "added": {added},
      "before": {get_current_total() - added},
      "after": {get_current_total()}
    }}
'''
            lines.insert(insert_marker, new_block.rstrip())
            with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        else:
            marker = '}  // end changelog'
            if marker in content:
                content = content.replace(marker,
                    f'    {{\n      "version": "{version}",\n      "date": "{now}",\n      "changes": ["{changes}"],\n      "added": {added}\n    }}\n  ],\n  {marker.strip()}')
                with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
                    f.write(content)
    except OSError as e:
        print(f"❌ Failed to write {CHANGELOG_PATH}: {e}")
        sys.exit(1)


def get_next_version() -> str:
    """Get next semantic version."""
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {META_PATH}: {e}")
        sys.exit(1)
    current = meta.get("version", "1.8.0")
    parts = current.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def get_current_total() -> int:
    """Get current keyword count."""
    try:
        count = 0
        for fp in glob.glob(f"{KEYWORDS_DIR}/*.json"):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    count += len(json.load(f))
            except (json.JSONDecodeError, OSError) as e:
                print(f"⚠️  Skipped {fp}: {e}")
        return count
    except Exception as e:
        print(f"❌ Failed counting keywords: {e}")
        sys.exit(1)


# ---------- commands ----------

def cmd_batch(args):
    """Process a batch JSON file of new keywords."""
    batch_file = args.file
    category = args.category
    subcategory = getattr(args, "subcategory", None)

    if not os.path.exists(batch_file):
        print(f"❌ File not found: {batch_file}")
        sys.exit(1)

    try:
        with open(batch_file, "r", encoding="utf-8") as f:
            new_items = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {batch_file}: {e}")
        sys.exit(1)
    if not isinstance(new_items, list):
        new_items = [new_items]

    # Validate required fields
    for item in new_items:
        for field in REQUIRED_FIELDS:
            if not item.get(field):
                print(f"❌ Missing required field '{field}' in item: {json.dumps(item, ensure_ascii=False)[:100]}")
                sys.exit(1)
        # Validate category
        try:
            with open("schema/keyword.schema.json", "r", encoding="utf-8") as f:
                valid_cats = json.load(f)["properties"]["category"]["enum"]
        except (json.JSONDecodeError, OSError) as e:
            print(f"❌ Failed to load schema: {e}")
            sys.exit(1)
        if item.get("category") not in valid_cats:
            print(f"❌ Invalid category '{item.get('category')}' in {item.get('id')}. Valid: {sorted(valid_cats)}")
            sys.exit(1)

    print(f"📦 Loaded {len(new_items)} new keyword(s) from {batch_file}")

    # Determine target file
    if category:
        target_cat = f"{KEYWORDS_DIR}/{category}.json"
    else:
        # Auto-detect: all items must share the same category
        cats_present = set(i.get("category") for i in new_items)
        if len(cats_present) > 1:
            print(f"❌ --category is required when new keywords span multiple categories: {sorted(cats_present)}")
            sys.exit(1)
        target_cat = f"{KEYWORDS_DIR}/{new_items[0].get('category')}.json"

    if not os.path.exists(target_cat):
        print(f"⚠️  Category file does not exist yet: {target_cat}")
        print("  It will be created with these keywords.")

    all_categories = load_all_categories()

    # Phase 1: Check for conflicts
    print("\n🔍 Checking for ID conflicts...")
    id_conflicts = check_id_conflicts(new_items, load_category(target_cat))
    if id_conflicts:
        print(f"  ❌ {len(id_conflicts)} ID conflict(s)!")
        for c in id_conflicts:
            print(f"    Existing: {c['existing'].get('id')} (term: {c['existing'].get('term')})")
            print(f"    New:      {c['new_id']} (term: {c['new_term']})")
            print("  → Resolve conflicts before adding. See https://github.com/zz3656/prompt-warehouse")
            if not args.force:
                sys.exit(1)
        print("  ⚠️  --force used, skipping ID conflicts.")
        # Remove conflicting items
        conflict_ids = {c["new_id"] for c in id_conflicts}
        new_items = [i for i in new_items if i.get("id") not in conflict_ids]

    # Phase 2: Check for term duplicates (within same category/subcategory)
    print("Checking for term duplicates...")
    term_dupes = check_term_dupes(new_items, all_categories)
    if term_dupes:
        print(f"  ⚠️  {len(term_dupes)} term duplicate(s) in same category/subcategory:")
        for d in term_dupes:
            print(f"    term='{d['term']}' in {d['category']}/{d['subcat']}")
            print(f"    existing: {d['existing']} (zh: {d['exist_zh']})")
            print(f"    new:      {d['new']} (zh: {d['new_zh']})")
        print("  → These are exact duplicates. Check if you meant to add a new keyword or update an existing one.")
        if not args.force:
            sys.exit(1)
        print("  ⚠️  --force used, skipping term duplicates.")

    # Phase 3: Check for similar terms
    print("Checking for similar terms (high similarity)...")
    similar = check_similar_terms(new_items, all_categories)
    if similar:
        print(f"  ⚠️  {len(similar)} keyword(s) have similar terms:")
        for s in similar:
            print(f"    {s['new_id']}: '{s['new_term']}'")
            for m in s["matches"][:3]:
                print(f"      → similar: '{m['existing_term']}' (ratio: {m['ratio']:.2f}, id: {m['existing_id']})")

    # Phase 4: Merge
    target_cat_path = f"{KEYWORDS_DIR}/{category}.json" if category else f"{KEYWORDS_DIR}/{new_items[0].get('category')}.json"

    if args.dry_run:
        print(f"\n✅ DRY RUN — would add {len(new_items)} keyword(s) to {target_cat_path}")
        print(f"  Current total: {get_current_total()}")
        print(f"  New total would be: {get_current_total() + len(new_items)}")
        print(f"  Version would bump: {get_next_version()}")
        for item in new_items[:5]:
            print(f"  • {item.get('id')}: {item.get('term')[:50]}")
        if len(new_items) > 5:
            print(f"  ... and {len(new_items) - 5} more")
        return

    # Actually merge
    merge_into_category(target_cat_path, new_items)
    print(f"\n✅ Added {len(new_items)} keyword(s) to {target_cat_path}")

    meta = update_meta()
    print(f"📊 Updated _meta.json: {meta['total_keywords']} total keywords (v{meta['version']})")

    index_info = update_index()
    print(f"🔎 Updated index: {index_info}")

    append_changelog(f"batch-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}", len(new_items), category)
    print(f"📝 Changelog updated (v{get_next_version()})")

    # Summary
    for item in new_items[:10]:
        print(f"  ✅ {item.get('id')}: {item.get('term')[:50]}")
    if len(new_items) > 10:
        print(f"  ... and {len(new_items) - 10} more")


def cmd_single(args):
    """Add a single keyword from command-line arguments."""
    term = args.term
    term_zh = getattr(args, "term_zh", None)
    category = args.category
    subcategory = getattr(args, "subcategory", "general")

    if not term or not category:
        print("❌ --term and --category are required for 'single' mode.")
        sys.exit(1)

    # Generate an ID from the category + subcategory + slug of term
    slug = re.sub(r'[^a-z0-9]+', '_', term.lower()).strip('_')
    if not slug:
        slug = "unknown"
    new_id = f"{category}_{subcategory}_{slug}"

    item = {
        "id": new_id,
        "term": term,
        "category": category,
        "subcategory": subcategory,
        "term_zh": term_zh,
        "labels": [],
        "labels_zh": [],
        "score": 0.5,
        "priority": "medium",
        "lifecycle": "approved",
        "tags": ["new"],
        "source": "manual",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if term_zh:
        item["term_zh"] = term_zh

    print(f"📝 New keyword:")
    print(f"  ID:    {new_id}")
    print(f"  term:  {term}")
    print(f"  term_zh: {term_zh or '(not provided)'}")
    print(f"  cat:   {category}/{subcategory}")

    # Use batch path with single-item file
    tmp_file = f"/tmp/new_single_{new_id}.json"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump([item], f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write temp file {tmp_file}: {e}")
        sys.exit(1)

    # Call batch with this temp file
    args.file = tmp_file
    args.force = False  # Don't force for single
    cmd_batch(args)


def cmd_template(args):
    """Output a template file for batch adding keywords."""
    template = {
        "description": "PWS keyword template — fill in each field. Delete fields you don't need.",
        "example": [
            {
                "id": "quality_basic_example",
                "term": "example term",
                "term_zh": "示例术语",
                "category": "quality",
                "subcategory": "basic",
                "labels": ["quality", "example"],
                "labels_zh": ["质量", "示例"],
                "aliases": ["another name", "synonym"],
                "aliases_zh": ["另一个名字", "同义词"],
                "score": 0.85,
                "priority": "high",
                "lifecycle": "approved",
                "tags": ["example"],
                "source": "manual",
                "notes": "Optional notes about this keyword.",
                "created_at": "2026-10-06T00:00:00+00:00",
                "updated_at": "2026-10-06T00:00:00+00:00",
                "usage_count": 0,
                "success_rate": None,
            }
        ],
        "fields": {
            "id": "Required. Format: {category}_{subcategory}_{slug}",
            "term": "Required. The English prompt term.",
            "term_zh": "Chinese translation (100% required).",
            "category": "Required. Must match schema enum.",
            "subcategory": "Required. Sub-category name.",
            "labels": "Optional. English search labels.",
            "labels_zh": "Optional. Chinese search labels (auto-generated if missing term_zh).",
            "aliases": "Optional. English synonyms.",
            "aliases_zh": "Optional. Chinese synonyms.",
            "score": "Optional. 0–1, default 0.5.",
            "priority": "Optional. high/medium/low/experimental, default medium.",
            "lifecycle": "Optional. draft/review/approved/deprecated/archived, default approved.",
            "tags": "Optional. User-defined tags.",
            "source": "Optional. Data source.",
            "notes": "Optional. Freeform notes.",
            "created_at": "Optional. ISO 8601 timestamp.",
            "updated_at": "Optional. ISO 8601 timestamp.",
            "usage_count": "Optional. Integer, default 0.",
            "success_rate": "Optional. 0–1 or null.",
        }
    }
    out = args.output if hasattr(args, 'output') and args.output else "batch_template.json"
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write template {out}: {e}")
        sys.exit(1)
    print(f"✅ Template written to {out}")
    print(f"   Edit the 'example' array with your keywords, then run:")
    print(f"   python3 tools/pws-add-new.py batch {out} --category <category>")


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(
        description="PWS Safe Keyword Ingestion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # batch
    batch_parser = subparsers.add_parser("batch", help="Add keywords from a JSON file")
    batch_parser.add_argument("file", help="Path to JSON file with new keywords (array)")
    batch_parser.add_argument("--category", required=True, help="Target category (e.g. quality, scene)")
    batch_parser.add_argument("--subcategory", help="Override subcategory for all items")
    batch_parser.add_argument("--dry-run", action="store_true", help="Preview only, no writes")
    batch_parser.add_argument("--force", action="store_true", help="Skip conflicts/duplicates, proceed anyway")

    # single
    single_parser = subparsers.add_parser("single", help="Add a single keyword from CLI args")
    single_parser.add_argument("--term", required=True, help="English prompt term")
    single_parser.add_argument("--term_zh", help="Chinese translation")
    single_parser.add_argument("--category", required=True, help="Target category")
    single_parser.add_argument("--subcategory", default="general", help="Target subcategory (default: general)")

    # template
    template_parser = subparsers.add_parser("template", help="Generate a batch template file")
    template_parser.add_argument("--output", default="batch_template.json", help="Output path")

    args = parser.parse_args()

    # Route to command
    if args.command == "batch":
        cmd_batch(args)
    elif args.command == "single":
        cmd_single(args)
    elif args.command == "template":
        cmd_template(args)


if __name__ == "__main__":
    main()
