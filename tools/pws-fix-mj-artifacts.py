#!/usr/bin/env python3
"""
pws-fix-mj-artifacts — Detect and fix MidJourney reference HTML/IMG scraping errors.

The willwulfken/MidJourney-Styles-and-Keywords-Reference repo originally shipped
HTML pages with embedded <Img> tags that sometimes leaked into scraped data,
producing values like:

    Crystalcore" Width="256" /> | <Img Src="/Images/Mj V5/V5 Alpha 1/...

This tool detects such artifacts and applies a conservative fix:
- Extracts the actual term word
- Updates labels to drop language-dependent fields
- Preserves source field for traceability

Usage:
  python3 tools/pws-fix-mj-artifacts.py                       # dry-run report
  python3 tools/pws-fix-mj-artifacts.py --apply               # fix all
  python3 tools/pws-fix-mj-artifacts.py --file keywords/categories/styles.json
  python3 tools/pws-fix-mj-artifacts.py --pattern 'html|pipe|prefix'  # filter by pattern
"""

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, asdict


@dataclass
class ArtifactIssue:
    file: str
    keyword_id: str
    field: str
    current_value: str
    pattern: str
    suggested_fix: str
    confidence: float  # 0..1


# Detection patterns with confidence levels (order matters: more specific first)
PATTERNS = [
    (re.compile(r'<\s*[A-Z][a-zA-Z]+\s+[^>]*>'), "html_tag", 0.95),
    (re.compile(r'<\s*/\s*[A-Z][a-zA-Z]*\s*>'), "closing_tag", 0.95),
    (re.compile(r'"\s*Width\s*=\s*"[^"]*"'), "width_attribute", 0.95),
    (re.compile(r'Src\s*=\s*"[^"]*"'), "image_src", 0.95),
    (re.compile(r'/Images/'), "image_path", 0.95),
    (re.compile(r'mj[ _]v5[ _].*?mj[ _]v5[ _]'), "double_mj_prefix", 0.90),
    (re.compile(r'\s+\|\s+'), "pipe_separator", 0.85),
]


def detect_artifacts_in_value(value: str) -> tuple[bool, str, float]:
    """Detect if a string value contains MJ scraping artifacts."""
    for pattern, name, confidence in PATTERNS:
        if pattern.search(value):
            return True, name, confidence
    return False, "", 0.0


def fix_artifact(value: str, pattern_name: str) -> str:
    """Generate a clean version of an artifact value."""
    if pattern_name in ("html_tag", "closing_tag"):
        # Remove everything starting from < onwards
        return value.split('<')[0].strip().rstrip('"')
    if pattern_name == "width_attribute":
        # Strategy: keep only the term-like leading content.
        # The term ends at the first " (quote), '<' (bracket), or 'Width='
        match = re.match(r'^([^\s"<]+(?:\s+[^\s"<]+)*?)(?=\s*"|\s*<|\s*Width\s*=|$)', value)
        if match:
            cleaned = match.group(1).strip().strip('"').strip()
        else:
            cleaned = value.split()[0] if value.split() else value
        # Also strip trailing pipe separators and beyond
        cleaned = cleaned.split(' | ')[0].strip().strip('"').strip()
        return cleaned
    if pattern_name == "pipe_separator":
        # Keep only the first segment before " | "
        return value.split(' | ')[0].strip()
    if pattern_name == "double_mj_prefix":
        # Strip everything from the second mj_v5_ occurrence
        # e.g. "mj_v5_themes_mj_v5_design_foo" -> "mj_v5_themes"
        # e.g. "mj v5 themes mj v5 design foo" -> "mj v5 themes"
        cleaned = re.split(r'mj[ _]v5[ _]', value)
        if len(cleaned) >= 3:
            # cleaned = ['prefix_', 'themes_', 'design_foo']
            prefix = cleaned[0]
            first_segment = cleaned[1]
            # Reconstruct "mj v5" + first segment
            sep = '_' if '_' in value else ' '
            return f"mj{sep}v5{sep}{first_segment}".rstrip('_').rstrip(' ')
        return value
    if pattern_name in ("image_src", "image_path"):
        # Strip any HTML/image path fragments and keep only the leading word(s)
        match = re.match(r'^([^\s"<]+(?:\s+[^\s"<]+)*?)(?=\s*"|\s*<|\s*Src\s*=|\s*/|$)', value)
        if match:
            cleaned = match.group(1).strip().strip('"').strip()
        else:
            cleaned = value.split()[0] if value.split() else value
        cleaned = cleaned.split('|')[0].strip().rstrip('"').strip().rstrip('/').strip()
        return cleaned or value.split()[0].strip()
    return value[:30].strip()


def scan_file(file_path: str) -> list[ArtifactIssue]:
    """Scan a single file for artifact issues."""
    issues = []
    data = json.load(open(file_path))
    if not isinstance(data, list):
        data = [data]

    for item in data:
        for field in ("term", "term_zh", "alias", "aliases_zh"):
            value = item.get(field)
            if not value:
                continue
            if isinstance(value, list):
                values = [(i, v) for i, v in enumerate(value)]
            else:
                values = [(None, value)]

            for idx, val in values:
                found, pattern_name, confidence = detect_artifacts_in_value(val)
                if found:
                    fixed = fix_artifact(val, pattern_name)
                    issues.append(ArtifactIssue(
                        file=os.path.relpath(file_path),
                        keyword_id=item.get("id", "?"),
                        field=f"{field}[{idx}]" if idx is not None else field,
                        current_value=val[:80],
                        pattern=pattern_name,
                        suggested_fix=fixed,
                        confidence=confidence
                    ))

    return issues


def apply_fixes(issues: list[ArtifactIssue]) -> int:
    """Apply fixes to source files."""
    fixes = 0
    by_file = {}
    for issue in issues:
        by_file.setdefault(issue.file, []).append(issue)

    for fp, file_issues in by_file.items():
        data = json.load(open(fp))
        if not isinstance(data, list):
            data = [data]

        # Index by id and field
        issue_index = {}
        for issue in file_issues:
            issue_index[(issue["id"], issue["field"])] = issue["suggested_fix"]

        for item in data:
            kid = item.get("id", "?")
            # Process term
            key = (kid, "term")
            if key in issue_index and item.get("term"):
                item["term"] = issue_index[key]
                fixes += 1

            # Process aliases (array)
            aliases = item.get("aliases", [])
            for i in range(len(aliases)):
                key = (kid, f"aliases[{i}]")
                if key in issue_index:
                    aliases[i] = issue_index[key]
                    fixes += 1

        with open(fp, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

    return fixes


def report(issues: list[ArtifactIssue]):
    """Print report of detected artifacts."""
    if not issues:
        print("✅ No MJ scraping artifacts found.")
        return

    print(f"\n{'=' * 70}")
    print(f"  MJ Artifact Scan — {len(issues)} issue(s) found")
    print(f"{'=' * 70}")

    by_pattern = {}
    for issue in issues:
        by_pattern.setdefault(issue.pattern, []).append(issue)

    for pattern, group in sorted(by_pattern.items(), key=lambda x: -len(x[1])):
        print(f"\n  📋 {pattern} ({sum(i.confidence for i in group)/len(group):.0%} confidence): {len(group)} issue(s)")
        for issue in group[:5]:
            print(f"    [{issue.keyword_id}] {issue.file}")
            print(f"      current:  {issue.current_value}")
            print(f"      fix:      {issue.suggested_fix}")

    print(f"\n  💡 Run with --apply to apply fixes")


def main():
    parser = argparse.ArgumentParser(
        description="Detect and fix MJ scraping artifacts in PWS data"
    )
    parser.add_argument("--apply", action="store_true", help="Apply fixes automatically")
    parser.add_argument("--file", type=str, help="Scan only this file")
    parser.add_argument("--report", type=str, help="Save JSON report to this path")
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = glob.glob("keywords/categories/*.json")

    issues = []
    for fp in sorted(files):
        issues.extend(scan_file(fp))

    report(issues)

    if args.report:
        with open(args.report, 'w') as f:
            json.dump({
                "version": "1.0",
                "total_issues": len(issues),
                "issues": [asdict(i) for i in issues]
            }, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Report saved to {args.report}")

    if args.apply and issues:
        fixes = apply_fixes(issues)
        print(f"\n✅ Applied {fixes} fix(es).")


if __name__ == "__main__":
    main()