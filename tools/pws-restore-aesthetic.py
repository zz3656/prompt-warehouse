#!/usr/bin/env python3
"""
pws-restore-aesthetic — Restore 9 mistakenly-skipped aesthetic words
from .bak-consolidation/aesthetic.json to current styles.json/aesthetic
and character.json/mood.

Also fixes 3 ID duplicates in styles.json.
"""

import json
import re
import sys
from datetime import datetime, timezone
from collections import Counter

CATEGORIES_DIR = "keywords/categories"


def safe_load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)


def safe_write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write {path}: {e}")
        sys.exit(1)


def slugify(text):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:40]


def build_new_id(target_cat, target_sub, term, existing_ids):
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


def main():
    # Step 1: load current target files
    styles = safe_load_json(f"{CATEGORIES_DIR}/styles.json")
    character = safe_load_json(f"{CATEGORIES_DIR}/character.json")

    existing_styles_ids = {s.get("id") for s in styles if s.get("id")}
    existing_char_ids = {c.get("id") for c in character if c.get("id")}

    # Step 2: load backup aesthetic
    backup_aesthetic = safe_load_json(f"{CATEGORIES_DIR}/.bak-consolidation/aesthetic.json")

    era_items = [x for x in backup_aesthetic if x.get("subcategory") == "era"]
    mood_items = [x for x in backup_aesthetic if x.get("subcategory") == "mood"]

    print(f"Restoring {len(era_items)} era words → styles.json/aesthetic")
    print(f"Restoring {len(mood_items)} mood words → character.json/mood")

    now = datetime.now(timezone.utc).isoformat()

    # Restore era → styles.json/aesthetic
    for item in era_items:
        new_item = dict(item)
        new_item["category"] = "styles"
        new_item["subcategory"] = "aesthetic"
        new_item["id"] = build_new_id("styles", "aesthetic", new_item.get("term", ""), existing_styles_ids)
        existing_styles_ids.add(new_item["id"])
        new_item["updated_at"] = now
        styles.append(new_item)
        print(f"  + styles/aesthetic: {new_item['id']}: {new_item['term']!r}")

    # Restore mood → character.json/mood
    for item in mood_items:
        new_item = dict(item)
        new_item["category"] = "character"
        new_item["subcategory"] = "mood"
        new_item["id"] = build_new_id("character", "mood", new_item.get("term", ""), existing_char_ids)
        existing_char_ids.add(new_item["id"])
        new_item["updated_at"] = now
        character.append(new_item)
        print(f"  + character/mood: {new_item['id']}: {new_item['term']!r}")

    # Step 3: Fix ID duplicates in styles.json
    print("\n--- Fixing ID duplicates in styles.json ---")
    id_counter = Counter()
    for s in styles:
        iid = s.get("id")
        if iid:
            id_counter[iid] += 1

    dup_ids = [iid for iid, c in id_counter.items() if c > 1]
    print(f"Found {len(dup_ids)} duplicate IDs: {dup_ids}")

    # Fix by adding _2 suffix to duplicates (keep first occurrence, suffix the rest)
    seen = set()
    for s in styles:
        iid = s.get("id")
        if not iid:
            continue
        if iid in seen:
            # Duplicate, find next available id
            base = iid
            new_id = f"{base}_2"
            n = 3
            while new_id in seen or new_id in existing_styles_ids:
                new_id = f"{base}_{n}"
                n += 1
            print(f"  ⚠️  Renaming duplicate id: {iid} → {new_id} (term: {s.get('term')!r})")
            s["id"] = new_id
            s["updated_at"] = now
        seen.add(s.get("id"))

    # Step 4: write back
    safe_write_json(f"{CATEGORIES_DIR}/styles.json", styles)
    safe_write_json(f"{CATEGORIES_DIR}/character.json", character)

    print(f"\n✅ Restored {len(era_items) + len(mood_items)} words, fixed {len(dup_ids)} ID duplicates")
    print(f"   styles.json: {len(styles)} keywords")
    print(f"   character.json: {len(character)} keywords")


if __name__ == "__main__":
    main()
