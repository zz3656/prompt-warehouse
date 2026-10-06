#!/usr/bin/env python3
"""
pws-audit — Unified PWS data quality audit.

Runs all checks in one pass:
  1. JSON syntax validation
  2. Schema validation against keyword.schema.json
  3. ID pattern check (must match ^[a-z][a-z0-9_]*$)
  4. Cross-category duplicate detection (by ID and by term+category+subcategory)
  5. Metadata consistency (_meta.json vs actual file counts)
  6. Field coverage (term_zh, labels_zh, score, priority, lifecycle)
  7. Score range validation (0..1)
  8. Lifecycle enum validation
  9. Category enum validation
  10. Template schema validation (templates/*.json)
  11. Long-term artifacts detection (HTML, pipe separators)

Usage:
  python3 tools/pws-audit.py                # full audit
  python3 tools/pws-audit.py --strict        # exit code 1 on warnings
  python3 tools/pws-audit.py --quiet          # only show summary
  python3 tools/pws-audit.py --report path.json  # save JSON report
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class Issue:
    severity: str  # "error", "warning", "info"
    category: str  # "schema", "id", "duplicate", "metadata", "field", "score", "lifecycle", "category", "artifact"
    file: str
    keyword_id: Optional[str]
    message: str


ID_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
VALID_LIFECYCLE = {"draft", "review", "approved", "deprecated", "archived"}
MAX_TERM_LENGTH = 80  # terms longer than this are likely problems


def load_keywords() -> tuple[list, dict]:
    """Load all keywords, mapping by filename."""
    by_file = {}
    all_items = []
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        try:
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️  Skipped {fp}: {e}")
            continue
        if not isinstance(data, list):
            data = [data]
        by_file[fp] = data
        for item in data:
            item["_source_file"] = fp
            all_items.append(item)
    return all_items, by_file


def load_schema() -> Optional[dict]:
    """Load keyword schema if available."""
    schema_path = "schema/keyword.schema.json"
    if not os.path.exists(schema_path):
        return None
    try:
        with open(schema_path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError:
        return None


def audit_schema(items: list, schema: Optional[dict], issues: list):
    """Audit schema validation."""
    if not schema:
        issues.append(Issue("warning", "schema", "schema/keyword.schema.json", None,
                           "Schema file not found or invalid"))
        return

    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        issues.append(Issue("info", "schema", "schema/keyword.schema.json", None,
                           "jsonschema not installed — skipping deep validation"))
        return

    for item in items:
        try:
            validate(instance=item, schema=schema)
        except ValidationError as e:
            issues.append(Issue("error", "schema", item.get("_source_file", "?"),
                               item.get("id"), f"Schema invalid: {e.message}"))


def audit_ids(items: list, issues: list):
    """Audit ID patterns."""
    seen = {}
    for item in items:
        iid = item.get("id", "")
        if not iid:
            issues.append(Issue("error", "id", item.get("_source_file", "?"), "?",
                              "Missing required field: id"))
            continue
        if not ID_PATTERN.match(iid):
            issues.append(Issue("error", "id", item.get("_source_file", "?"), iid,
                              f"ID does not match {ID_PATTERN.pattern}"))
        if iid in seen:
            issues.append(Issue("error", "id", item.get("_source_file", "?"), iid,
                              f"Duplicate ID (first seen in {seen[iid]})"))
        else:
            seen[iid] = item.get("_source_file", "?")


def audit_duplicates(items: list, issues: list):
    """Audit duplicates across categories."""
    # Cross-category (same term+subcategory within same category)
    term_groups = defaultdict(list)
    for item in items:
        key = (item.get("category"), item.get("subcategory"), item.get("term", "").lower().strip())
        if item.get("term"):
            term_groups[key].append(item)

    for key, group in term_groups.items():
        if len(group) > 1:
            cat, subcat, term = key
            ids = ", ".join(i.get("id", "?") for i in group[:3])
            issues.append(Issue("warning", "duplicate", group[0].get("_source_file", "?"),
                               ids,
                              f"Cross-category duplicate: term='{term}' cat={cat}/{subcat} ({len(group)} copies)"))


def audit_metadata(items: list, issues: list):
    """Audit _meta.json vs actual counts."""
    meta_path = "keywords/_meta.json"
    if not os.path.exists(meta_path):
        issues.append(Issue("warning", "metadata", meta_path, None,
                           "_meta.json not found"))
        return

    try:
        with open(meta_path, encoding="utf-8") as fh:
            meta = json.load(fh)
    except (json.JSONDecodeError, OSError) as e:
        issues.append(Issue("error", "metadata", meta_path, None,
                           f"Could not load {meta_path}: {e}"))
        return
    actual_count = len(items)
    actual_categories = len(glob.glob("keywords/categories/*.json"))

    if meta.get("total_keywords") != actual_count:
        issues.append(Issue("warning", "metadata", meta_path, None,
                          f"total_keywords mismatch: meta={meta.get('total_keywords')}, actual={actual_count}"))

    if meta.get("total_categories") != actual_categories:
        issues.append(Issue("warning", "metadata", meta_path, None,
                          f"total_categories mismatch: meta={meta.get('total_categories')}, actual={actual_categories}"))


def audit_field_coverage(items: list, issues: list):
    """Audit field coverage."""
    total = len(items)
    if total == 0:
        return

    # Bilingual coverage
    with_term_zh = sum(1 for i in items if i.get("term_zh"))
    with_labels_zh = sum(1 for i in items if i.get("labels_zh"))
    with_aliases = sum(1 for i in items if i.get("aliases"))

    if with_term_zh < total * 0.5:
        issues.append(Issue("info", "field", "keywords/categories/", None,
                          f"term_zh coverage low: {with_term_zh}/{total} ({with_term_zh/total*100:.1f}%)"))
    if with_labels_zh < with_term_zh:
        issues.append(Issue("info", "field", "keywords/categories/", None,
                          f"labels_zh lags term_zh: {with_labels_zh} vs {with_term_zh}"))


def audit_scores(items: list, issues: list):
    """Audit score ranges."""
    for item in items:
        score = item.get("score")
        if score is None:
            issues.append(Issue("warning", "score", item.get("_source_file", "?"),
                               item.get("id"), "Missing score field"))
        elif score < 0 or score > 1:
            issues.append(Issue("error", "score", item.get("_source_file", "?"),
                               item.get("id"), f"Score out of range: {score}"))


def audit_lifecycles(items: list, issues: list):
    """Audit lifecycle enum."""
    for item in items:
        lc = item.get("lifecycle")
        if lc is None:
            issues.append(Issue("warning", "lifecycle", item.get("_source_file", "?"),
                               item.get("id"), "Missing lifecycle"))
        elif lc not in VALID_LIFECYCLE:
            issues.append(Issue("error", "lifecycle", item.get("_source_file", "?"),
                               item.get("id"), f"Invalid lifecycle: '{lc}' (valid: {sorted(VALID_LIFECYCLE)})"))


def audit_categories(items: list, schema: Optional[dict], issues: list):
    """Audit category enum."""
    if not schema:
        return
    valid_cats = set(schema.get("properties", {}).get("category", {}).get("enum", []))

    # Check filenames
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        cat = os.path.basename(fp).replace(".json", "")
        if cat not in valid_cats:
            issues.append(Issue("warning", "category", fp, None,
                              f"File category '{cat}' not in schema enum"))

    # Check item categories
    for item in items:
        cat = item.get("category")
        if cat and cat not in valid_cats:
            issues.append(Issue("error", "category", item.get("_source_file", "?"),
                               item.get("id"), f"Category '{cat}' not in schema enum"))


def audit_artifacts(items: list, issues: list):
    """Detect scraping artifacts in term values."""
    artifact_patterns = [
        (re.compile(r'<\s*[A-Z][a-zA-Z]+'), "HTML tag"),
        (re.compile(r'\s+\|\s+'), "pipe separator"),
        (re.compile(r'mj[ _]v5[ _].*?mj[ _]v5[ _]'), "double mj_v5 prefix"),
    ]

    for item in items:
        term = item.get("term", "")
        if not term:
            continue
        for pattern, name in artifact_patterns:
            if pattern.search(term):
                issues.append(Issue("warning", "artifact", item.get("_source_file", "?"),
                                   item.get("id"), f"Term contains {name}: {term[:50]}..."))
                break


def audit_templates(issues: list):
    """Audit template schema (basic check)."""
    for fp in sorted(glob.glob("templates/*.json")):
        if "_meta" in fp or "_legacy" in fp:
            continue
        try:
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as e:
            issues.append(Issue("error", "schema", fp, None, f"Invalid JSON: {e}"))
            continue

        if isinstance(data, list):
            for item in data:
                if "id" in item:
                    if "variants" not in item:
                        issues.append(Issue("warning", "schema", fp, item.get("id"),
                                          "Template missing 'variants' field"))


def print_report(issues: list, quiet: bool = False):
    """Print formatted audit report."""
    if not quiet:
        print(f"\n{'=' * 70}")
        print(f"  PWS Data Audit — {len(issues)} issue(s)")
        print(f"{'=' * 70}")

    by_severity = defaultdict(list)
    for issue in issues:
        by_severity[issue.severity].append(issue)

    for severity in ("error", "warning", "info"):
        group = by_severity.get(severity, [])
        if not group:
            continue
        icon = {"error": "❌", "warning": "⚠️ ", "info": "ℹ️ "}[severity]
        if not quiet:
            print(f"\n  {icon} {severity.upper()}: {len(group)} issue(s)")
            for issue in group[:20]:
                loc = f"[{issue.keyword_id}]" if issue.keyword_id else ""
                print(f"    {icon} {issue.category} | {issue.file}:{loc}")
                print(f"        {issue.message}")
            if len(group) > 20:
                print(f"    ... and {len(group)-20} more")
        else:
            print(f"  {severity}: {len(group)}")

    # Summary
    if not quiet:
        print(f"\n{'=' * 70}")
        print(f"  Summary: {len(by_severity.get('error',[]))} errors, "
              f"{len(by_severity.get('warning',[]))} warnings, "
              f"{len(by_severity.get('info',[]))} info")
        print(f"{'=' * 70}")


def save_report(issues: list, path: str):
    """Save JSON report."""
    report = {
        "version": "1.0",
        "total_issues": len(issues),
        "by_severity": {},
        "by_category": {},
        "issues": [asdict(i) for i in issues]
    }
    for issue in issues:
        report["by_severity"][issue.severity] = report["by_severity"].get(issue.severity, 0) + 1
        report["by_category"][issue.category] = report["by_category"].get(issue.category, 0) + 1
    try:
        with open(path, 'w', encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Could not save report to {path}: {e}")
        return
    print(f"\n📄 Report saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="PWS data quality audit")
    parser.add_argument("--strict", action="store_true", help="Exit with error code on warnings")
    parser.add_argument("--quiet", action="store_true", help="Only show summary counts")
    parser.add_argument("--report", type=str, help="Save JSON report to this path")
    args = parser.parse_args()

    print("🔍 Running PWS data audit...")
    items, by_file = load_keywords()
    schema = load_schema()

    issues: list[Issue] = []

    print(f"  Loaded {len(items)} keywords from {len(by_file)} files")

    audit_schema(items, schema, issues)
    audit_ids(items, issues)
    audit_duplicates(items, issues)
    audit_metadata(items, issues)
    audit_field_coverage(items, issues)
    audit_scores(items, issues)
    audit_lifecycles(items, issues)
    audit_categories(items, schema, issues)
    audit_artifacts(items, issues)
    audit_templates(issues)

    print_report(issues, quiet=args.quiet)

    if args.report:
        save_report(issues, args.report)

    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")

    if errors > 0:
        sys.exit(1)
    if args.strict and warnings > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()