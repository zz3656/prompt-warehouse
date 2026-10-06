#!/usr/bin/env python3
"""
pws-translate — Prompt Warehouse 批量翻译工具

为关键词/模板的 term_zh, aliases_zh, labels_zh 字段补充中文翻译。

使用方法:
  1. 全自动模式（推荐）: 读取现有数据，生成翻译 JSON 映射，写入回文件
     python3 tools/pws-translate.py --translate-all --dry-run
     python3 tools/pws-translate.py --translate-all

  2. 指定文件模式:
     python3 tools/pws-translate.py --file keywords/categories/quality.json --dry-run
     python3 tools/pws-translate.py --file keywords/categories/quality.json

  3. 手动输入翻译模式（交互式）:
     python3 tools/pws-translate.py --interactive

  4. 仅生成翻译草稿（不写入，供人工审查）:
     python3 tools/pws-translate.py --generate-draft output/draft_translations.json

翻译数据写入 JSONL 格式的 _translations.jsonl 索引，便于后续人工审核和修改。
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher

# ---------- configuration ----------

TRANSLATIONS_INDEX = "_translations.jsonl"

# Pre-defined translation mappings for commonly used terms.
# Loaded from tools/data/pre_translations.json (git-tracked data file, 326KB).
# To add new entries, edit tools/data/pre_translations.json directly — entries
# are sorted alphabetically for predictable diffs and conflict resolution.
_PRE_TRANSLATIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "pre_translations.json"
)
try:
    with open(_PRE_TRANSLATIONS_PATH, encoding="utf-8") as _f:
        PRE_TRANSLATIONS = json.load(_f)
except FileNotFoundError:
    sys.stderr.write(
        f"ERROR: pre_translations.json not found at {_PRE_TRANSLATIONS_PATH}\n"
        "Did you delete tools/data/ ? Restore from git history.\n"
    )
    sys.exit(2)
del _PRE_TRANSLATIONS_PATH, _f
# Marker preserved for compatibility with any external code referencing the dict name.
def safe_load_json(path: str) -> dict:
    """Load a JSON file with error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)


def load_index():
    """Load the _translations.jsonl index."""
    index_path = os.path.join("keywords", TRANSLATIONS_INDEX)
    entries = []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Could not read translation index: {e}")
    return entries


def save_index(entries):
    """Save the _translations.jsonl index."""
    index_path = os.path.join("keywords", TRANSLATIONS_INDEX)
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"❌ Failed to write translation index: {e}")
        sys.exit(1)


def load_all_keywords():
    """Load ALL keywords from all category files."""
    all_kws = []
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        data = safe_load_json(fp)
        for item in (data if isinstance(data, list) else [data]):
            item["_source_file"] = fp
            all_kws.append(item)
    return all_kws


def write_category_file(path, data):
    """Write back a category file, preserving format."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write {path}: {e}")
        sys.exit(1)


# ---------- translation engine ----------

def build_index(entries):
    """Build a fast lookup: term_lower -> chinese_translation."""
    idx = {}
    for entry in entries:
        term = entry.get("term", "").lower()
        zh = entry.get("term_zh", "")
        if term and zh:
            idx[term] = zh
    return idx


def find_translation(term: str, index: dict) -> str | None:
    """Find Chinese translation for an English term.
    Priority: pre_translations > index > word_compose > similar_match > None
    """
    lower = term.lower().strip()

    # 1. Pre-defined (exact match)
    if lower in PRE_TRANSLATIONS:
        return PRE_TRANSLATIONS[lower]

    # 2. Index (exact match)
    if lower in index:
        return index[lower]

    # 3. Word-composition (try FIRST to handle "red hair blue eyes" properly)
    #    Translate compound terms word-by-word before attempting substring/fuzzy matches.
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]+", lower)
    if len(words) >= 2:
        translated_words = []
        matched_count = 0
        for word in words:
            if word in PRE_TRANSLATIONS:
                translated_words.append(PRE_TRANSLATIONS[word])
                matched_count += 1
            elif word in index:
                translated_words.append(index[word])
                matched_count += 1
            else:
                translated_words.append(None)

        # Use word-composition if >=60% of words translated AND >=2 words matched
        coverage = matched_count / max(len(words), 1)
        if matched_count >= 2 and coverage >= 0.6:
            composed = []
            for w, t in zip(words, translated_words, strict=True):
                if t is not None:
                    composed.append(t)
                else:
                    composed.append(w)  # fall back to original English
            return ''.join(composed)

    # 4. Substring match: find longest phrase from PRE_TRANSLATIONS contained in term
    #    Useful for descriptive terms like "a major earthquake violently shaking..."
    best_substr_len = 0
    best_substr_zh = None
    for key, zh in PRE_TRANSLATIONS.items():
        if ' ' in key and len(key) >= 8 and key in lower and len(key) > best_substr_len:
                best_substr_len = len(key)
                best_substr_zh = zh

    if best_substr_zh and best_substr_len >= 8:
        return best_substr_zh

    # 5. Fuzzy match (existing)
    best_sim = 0
    best_term = None
    for key in index:
        sim = SequenceMatcher(None, lower, key).ratio()
        if sim > best_sim and sim >= 0.85:
            best_sim = sim
            best_term = key

    if best_term:
        return index[best_term]

    return None


def collect_untranslated(all_kws):
    """Collect keywords that are missing term_zh."""
    untranslated = []
    for kw in all_kws:
        if not kw.get("term_zh"):
            untranslated.append(kw)
    return untranslated


def translate_batch(untranslated_kws, index):
    """Translate a batch of keywords. Returns (translated_items, untranslated_count)."""
    translated_count = 0
    for kw in untranslated_kws:
        term = kw.get("term", "").strip()
        if not term:
            continue

        zh = find_translation(term, index)
        if zh:
            kw["term_zh"] = zh
            kw["_translated_auto"] = True
            kw["_translated_at"] = datetime.now(timezone.utc).isoformat()
            translated_count += 1

    return translated_count


# ---------- interactive mode ----------

def interactive_translate(kw, index):
    """Ask user for translation of a single keyword."""
    term = kw.get("term", "")
    auto_zh = find_translation(term, index)

    print(f"\n[{kw.get('category', '?')}/{kw.get('subcategory', '?')}]")
    print(f"  term:   {term}")
    if auto_zh:
        print(f"  auto:   {auto_zh}  (enter to skip)")
    else:
        print("  auto:   (none found)")
    zh = input("  term_zh> ").strip()
    if zh:
        kw["term_zh"] = zh
        kw["_translated_manual"] = True
        kw["_translated_at"] = datetime.now(timezone.utc).isoformat()
        return True
    return False


# ---------- report ----------

def print_report(translated_count, skipped_count, total, file_counts):
    print("\n" + "=" * 60)
    print("  Translation Report")
    print("=" * 60)
    print(f"  Total keywords:     {total}")
    print(f"  Translated:         {translated_count}")
    print(f"  Untranslated:       {skipped_count}")
    if total:
        pct = translated_count / total * 100
        print(f"  Coverage:           {pct:.1f}%")
    print("\n  Files updated:")
    for fp, count in sorted(file_counts.items()):
        print(f"    {fp}: {count} keywords")
    print()


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="PWS Batch Translator")
    parser.add_argument("--translate-all", action="store_true", help="Translate all keyword files")
    parser.add_argument("--file", metavar="FILE", help="Translate a single file only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without writing")
    parser.add_argument("--generate-draft", metavar="FILE", help="Generate draft translation JSON for review")
    parser.add_argument("--interactive", action="store_true", help="Interactive manual translation mode")
    parser.add_argument("--force", action="store_true", help="Overwrite existing term_zh values")
    args = parser.parse_args()

    # Load existing translations index
    index_entries = load_index()
    index = build_index(index_entries)

    if args.generate_draft:
        # Generate draft for review
        kws = load_all_keywords() if not args.file else safe_load_json(args.file)
        if isinstance(kws, dict):
            kws = [kws]

        draft = {"generated_at": datetime.now(timezone.utc).isoformat(), "entries": []}
        for kw in kws:
            term = kw.get("term", "").strip()
            if not term:
                continue
            zh = find_translation(term, index)
            if zh:
                draft["entries"].append({
                    "id": kw.get("id", ""),
                    "term": term,
                    "term_zh": zh,
                    "category": kw.get("category", ""),
                    "subcategory": kw.get("subcategory", ""),
                })

        try:
            os.makedirs(os.path.dirname(args.generate_draft) or ".", exist_ok=True)
            with open(args.generate_draft, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"❌ Failed to write draft: {e}")
            sys.exit(1)
        print(f"Draft written to {args.generate_draft} ({len(draft['entries'])} entries)")
        return

    # Load keywords
    if args.translate_all:
        all_kws = load_all_keywords()
    elif args.file:
        all_kws = safe_load_json(args.file)
        if isinstance(all_kws, dict):
            all_kws = [all_kws]
        for kw in all_kws:
            kw["_source_file"] = args.file
    elif args.dry_run:
        # dry-run defaults to translate-all
        all_kws = load_all_keywords()
    else:
        print("Error: specify --translate-all or --file FILE", file=sys.stderr)
        sys.exit(1)

    # Filter untranslated
    if not args.force:
        kws_to_translate = [kw for kw in all_kws if not kw.get("term_zh")]
    else:
        kws_to_translate = all_kws

    if args.interactive:
        print(f"Interactive mode: {len(kws_to_translate)} keywords to translate\n")
        count = 0
        for kw in kws_to_translate:
            if interactive_translate(kw, index):
                count += 1
        print(f"\nManual translated: {count}/{len(kws_to_translate)}")
        return

    # Dry run mode
    if args.dry_run:
        # Make copies so we don't mutate originals
        copy_list = [dict(kw, _source_file=kw.get("_source_file", "")) for kw in kws_to_translate]
        translated_count = translate_batch(copy_list, index)
        print(f"DRY RUN: Would translate {translated_count}/{len(kws_to_translate)} keywords")

        # Show a sample (up to 15 translated ones)
        translated_samples = [kw for kw in copy_list if kw.get("term_zh")][:15]
        if translated_samples:
            print("\nSample translations:")
            for kw in translated_samples:
                print(f"  {kw.get('term')} -> {kw['term_zh']}")
        else:
            print("\n(Note: no auto-translations available in pre-defined dictionary)")
            print("Try: python3 tools/pws-translate.py --generate-draft output/draft.json")
        return

    # Full translate mode
    kw_list = list(kws_to_translate)
    translated_count = translate_batch(kw_list, index)
    skipped_count = len(kw_list) - translated_count

    # Save translation index
    for kw in kw_list:
        if kw.get("term_zh"):
            entry = {
                "term": kw.get("term", ""),
                "term_zh": kw["term_zh"],
                "id": kw.get("id", ""),
                "category": kw.get("category", ""),
                "updated_at": kw.get("_translated_at", datetime.now(timezone.utc).isoformat()),
            }
            # Only add if not already in index (avoid duplicates)
            existing_terms = {e["term"] for e in index_entries}
            if entry["term"] not in existing_terms:
                index_entries.append(entry)

    save_index(index_entries)

    # Write back to files
    file_counts = {}
    for kw in kw_list:
        if kw.get("term_zh"):
            src = kw.get("_source_file", "")
            if not src:
                continue
            file_counts[src] = file_counts.get(src, 0) + 1

            # Find and update in source data
            data = safe_load_json(src)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if item.get("id") == kw.get("id"):
                        data[i]["term_zh"] = kw["term_zh"]
                        if kw.get("updated_at"):
                            data[i]["updated_at"] = kw["updated_at"]
                        break
                write_category_file(src, data)

    print_report(translated_count, skipped_count, len(kws_to_translate), file_counts)


if __name__ == "__main__":
    main()
