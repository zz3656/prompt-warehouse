#!/usr/bin/env python3
"""
pws-dedup — Prompt Warehouse 去重工具

在补充新关键词/模板前运行此脚本，检测:
  1. ID 冲突 (exact match on id field)
  2. term 完全重复 (exact match on term field)
  3. term 相似重复 (Levenshtein distance <= 2 或 normalized similarity >= 0.9)
  4. 分类/子分类同名 (same term across different categories — flagged as warning)

Usage:
  python3 tools/pws-dedup.py --check keywords/categories/quality.json
  python3 tools/pws-dedup.py --check keywords/categories/quality.json --new quality_new.json
  python3 tools/pws-dedup.py --check keywords/categories/quality.json --new quality_new.json --auto-merge
  python3 tools/pws-dedup.py --scan-all --new keywords/categories/new_batch.json
  python3 tools/pws-dedup.py --check templates/h3_video_prompts.json
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

# ---------- levenshtein distance ----------

def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein distance between two lowercase strings."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    curr = [0] * (len(b) + 1)
    for i, ca in enumerate(a, 1):
        curr[0] = i
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev
    return prev[len(b)]


def similarity(a: str, b: str) -> float:
    """Normalized similarity in [0, 1]."""
    al, bl = len(a), len(b)
    if al == 0 and bl == 0:
        return 1.0
    dist = levenshtein(a.lower(), b.lower())
    max_len = max(al, bl)
    return 1.0 - dist / max_len


# ---------- load helpers ----------

def load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as e:
        print(f'Failed to load {path}: {e}')
        sys.exit(1)


def load_keywords_dir(pattern: str = "keywords/categories/*.json"):
    """Load ALL existing keywords into a flat list with source tracking."""
    all_kws = []
    for fp in sorted(glob.glob(pattern)):
        data = load_json(fp)
        for item in (data if isinstance(data, list) else [data]):
            item["_source_file"] = fp
            all_kws.append(item)
    return all_kws


def load_keywords_file(path: str):
    """Load keywords from a single file (list or wrapped single object)."""
    data = load_json(path)
    if isinstance(data, list):
        return data
    return [data]


def get_term(item):
    return (item.get("term") or "").strip().lower()


def get_id(item):
    return (item.get("id") or "").strip()


# ---------- dedup checks ----------

class DedupReport:
    def __init__(self):
        self.id_conflicts = []       # (new_item, existing_item, existing_file)
        self.term_exact = []         # (new_item, existing_item, existing_file)
        self.term_similar = []       # (new_item, existing_item, existing_file, sim_score)
        self.cross_cat_warn = []     # (new_item, existing_item, existing_file)

    def summary(self):
        lines = [
            f"ID conflicts:     {len(self.id_conflicts)}",
            f"Exact term dupes: {len(self.term_exact)}",
            f"Similar term dupes: {len(self.term_similar)}",
            f"Cross-category warnings: {len(self.cross_cat_warn)}",
        ]
        return "\n".join(lines)


def check_batch(new_kws, existing_kws):
    report = DedupReport()

    for new_item in new_kws:
        nid = get_id(new_item)
        nterm = get_term(new_item)

        for ex_item in existing_kws:
            eid = get_id(ex_item)
            eterm = get_term(ex_item)

            # 1. ID conflict
            if nid and eid and nid == eid:
                report.id_conflicts.append((new_item, ex_item, ex_item["_source_file"]))
                continue  # skip further checks on same item

            # 2. Exact term duplicate
            if nterm and eterm and nterm == eterm:
                report.term_exact.append((new_item, ex_item, ex_item["_source_file"]))
                continue

            # 3. Similar term
            if nterm and eterm and len(nterm) > 1 and len(eterm) > 1:
                sim = similarity(nterm, eterm)
                if sim >= 0.90:
                    report.term_similar.append((new_item, ex_item, ex_item["_source_file"], sim))
                    continue

            # 4. Cross-category (same term, different category)
            if nterm and eterm and nterm == eterm:
                nc = new_item.get("category", "")
                ec = ex_item.get("category", "")
                if nc and ec and nc != ec:
                    report.cross_cat_warn.append((new_item, ex_item, ex_item["_source_file"]))

    return report


# ---------- auto-merge ----------

def auto_merge_term_zh(new_item, existing_item):
    """When term is a duplicate but new_item may have term_zh, copy it to existing."""
    updated = False
    merged = dict(existing_item)

    # Copy term_zh if new has it and existing doesn't
    if new_item.get("term_zh") and not existing_item.get("term_zh"):
        merged["term_zh"] = new_item["term_zh"]
        updated = True

    if new_item.get("aliases_zh") and not existing_item.get("aliases_zh"):
        merged["aliases_zh"] = new_item["aliases_zh"]
        updated = True

    if new_item.get("labels_zh") and not existing_item.get("labels_zh"):
        merged["labels_zh"] = new_item["labels_zh"]
        updated = True

    # Merge labels (union)
    new_labels = set(new_item.get("labels", []))
    old_labels = set(merged.get("labels", []))
    if new_labels - old_labels:
        merged["labels"] = sorted(old_labels | new_labels)
        updated = True

    # Update timestamps
    merged["updated_at"] = datetime.now(timezone.utc).isoformat()

    return merged, updated


def auto_merge_file(file_path, existing_kws_by_id, existing_kws_by_term):
    """Read new batch from file, merge into existing, write back."""
    new_kws = load_keywords_file(file_path)
    updated_files = {}
    changes_made = 0

    for new_item in new_kws:
        nid = get_id(new_item)
        nterm = get_term(new_item)

        # Check by ID
        if nid in existing_kws_by_id:
            old = existing_kws_by_id[nid]
            merged, changed = auto_merge_term_zh(new_item, old)
            if changed:
                src = old["_source_file"]
                updated_files.setdefault(src, [])
                updated_files[src].append(merged)
                changes_made += 1
                # Also update the by-term index
                if nterm:
                    existing_kws_by_term[nterm] = merged

        # Check by term (if no ID match)
        elif nterm and nterm in existing_kws_by_term:
            old = existing_kws_by_term[nterm]
            merged, changed = auto_merge_term_zh(new_item, old)
            if changed:
                src = old["_source_file"]
                updated_files.setdefault(src, [])
                updated_files[src].append(merged)
                changes_made += 1

    # Write back updated files
    for fp, items in updated_files.items():
        data = load_json(fp)
        if isinstance(data, list):
            # Replace matching items in-place
            data_ids = {i.get("id") for i in data}
            new_ids = {i.get("id") for i in items}
            # items may reference same objects; rebuild
            for i, item in enumerate(data):
                for merged in items:
                    if item.get("id") == merged.get("id"):
                        data[i] = merged
                        break
            write_json(fp, data)
        else:
            write_json(fp, data)

    return changes_made, updated_files


def write_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    except OSError as e:
        print(f"Failed to write {path}: {e}")
        sys.exit(1)


# ---------- display helpers ----------

def print_report(report: DedupReport):
    print("=" * 70)
    print("  PWS Dedup Report")
    print("=" * 70)
    print(report.summary())
    print()

    if report.id_conflicts:
        print("🔴 ID CONFLICTS (same id exists):")
        for new, old, fp in report.id_conflicts:
            print(f"  id: {get_id(new)}")
            print(f"    new:    {get_term(new)}  (term_zh: {new.get('term_zh', '-')})")
            print(f"    exist:  {get_term(old)}  (file: {fp})")
            print()

    if report.term_exact:
        print("🔴 EXACT TERM DUPLICATES (same term text):")
        for new, old, fp in report.term_exact:
            print(f"  term: {get_term(new)}")
            print(f"    new:    id={get_id(new)}  cat={new.get('category')}  term_zh={new.get('term_zh', '-')}")
            print(f"    exist:  id={get_id(old)}  cat={old.get('category')}  term_zh={old.get('term_zh', '-')}  file={fp}")
            print()

    if report.term_similar:
        print("🟡 SIMILAR TERM DUPLICATES (similarity >= 0.90):")
        for new, old, fp, sim in report.term_similar:
            print(f"  {get_term(new)}  <->  {get_term(old)}  (sim={sim:.2f})")
            print(f"    new:    id={get_id(new)}  term_zh={new.get('term_zh', '-')}")
            print(f"    exist:  id={get_id(old)}  term_zh={old.get('term_zh', '-')}  file={fp}")
            print()

    if report.cross_cat_warn:
        print("⚠️  CROSS-CATEGORY (same term in different categories):")
        for new, old, fp in report.cross_cat_warn:
            print(f"  term: {get_term(new)}  cat={new.get('category')} vs {old.get('category')}  file={fp}")
            print()

    if not any([report.id_conflicts, report.term_exact, report.term_similar, report.cross_cat_warn]):
        print("✅ No duplicates found. Safe to add.")
        print()


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="PWS Deduplication Tool")
    parser.add_argument("--check", metavar="FILE", help="Existing category file to check against")
    parser.add_argument("--scan-all", action="store_true", help="Scan ALL keyword categories (auto-populate --check source)")
    parser.add_argument("--new", metavar="FILE", help="New batch file to check/merge")
    parser.add_argument("--auto-merge", action="store_true", help="Auto-merge term_zh into existing entries on exact duplicates")
    parser.add_argument("--dedup-only", metavar="FILE", help="Run dedup on a single file internally (check within itself)")
    parser.add_argument("--format-report", action="store_true", help="Output as JSON for programmatic consumption")
    parser.add_argument("--quiet", action="store_true", help="Only output errors")
    args = parser.parse_args()

    if args.format_report and not any([args.check, args.scan_all, args.dedup_only]):
        print("Error: --format-report requires --check, --scan-all, or --dedup-only", file=sys.stderr)
        sys.exit(1)

    report = DedupReport()

    # Mode 1: dedup within a single file
    if args.dedup_only:
        kws = load_keywords_file(args.dedup_only)
        existing = []
        for item in kws:
            nid = get_id(item)
            nterm = get_term(item)
            for ex in existing:
                eid = get_id(ex)
                eterm = get_term(ex)
                if nid == eid:
                    report.id_conflicts.append((item, ex, args.dedup_only))
                if nterm == eterm:
                    report.term_exact.append((item, ex, args.dedup_only))
            existing.append(item)
        if not args.quiet:
            print_report(report)
        else:
            print(json.dumps({"id_conflicts": len(report.id_conflicts), "term_exact": len(report.term_exact)}))
        if report.id_conflicts or report.term_exact:
            sys.exit(1)
        return

    # Determine existing keywords
    existing_kws = []
    if args.scan_all:
        existing_kws = load_keywords_dir()
    elif args.check:
        existing_kws = load_keywords_file(args.check)
    # Add _source_file tracking
    for kw in existing_kws:
        kw.setdefault("_source_file", args.check)

    if not existing_kws:
        print("Error: No existing keywords loaded", file=sys.stderr)
        sys.exit(1)

    # Build lookup indices
    existing_by_id = {}
    existing_by_term = {}
    for kw in existing_kws:
        kid = get_id(kw)
        kterm = get_term(kw)
        if kid:
            existing_by_id[kid] = kw
        if kterm:
            existing_by_term[kterm] = kw

    # Mode 2: check new file against existing
    if args.new:
        new_kws = load_keywords_file(args.new)

        # First, run dedup checks
        report = check_batch(new_kws, existing_kws)

        # Report format output
        if args.format_report:
            out = {
                "id_conflicts": [{"new_id": get_id(n), "new_term": get_term(n), "exist_id": get_id(e), "exist_term": get_term(e), "file": fp} for n, e, fp in report.id_conflicts],
                "term_exact": [{"new_id": get_id(n), "new_term": get_term(n), "exist_id": get_id(e), "exist_term": get_term(e), "new_cat": n.get("category"), "exist_cat": e.get("category"), "file": fp} for n, e, fp in report.term_exact],
                "term_similar": [{"new_term": get_term(n), "exist_term": get_term(e), "similarity": round(s, 3), "exist_id": get_id(e), "file": fp} for n, e, fp, s in report.term_similar],
                "cross_category": [{"term": get_term(n), "new_cat": n.get("category"), "exist_cat": e.get("category"), "file": fp} for n, e, fp in report.cross_cat_warn],
                "summary": report.summary(),
            }
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print_report(report)

        # Auto-merge mode
        if args.auto_merge:
            changes, files = auto_merge_file(args.new, existing_by_id, existing_by_term)
            print(f"Auto-merge: {changes} fields updated across {len(files)} files")
            for fp in files:
                print(f"  Updated: {fp}")
        return

    print("Usage: python3 tools/pws-dedup.py --check FILE --new NEW_FILE")
    print("       python3 tools/pws-dedup.py --scan-all --new NEW_FILE")
    print("       python3 tools/pws-dedup.py --dedup-only FILE")
    print("       python3 tools/pws-dedup.py --dedup-only FILE --format-report")
    sys.exit(1)


if __name__ == "__main__":
    main()
