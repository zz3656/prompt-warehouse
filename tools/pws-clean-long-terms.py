#!/usr/bin/env python3
"""
pws-clean-long-terms — Detect and fix long/corrupted term values in PWS keyword data.

Finds terms that are abnormally long (>40 chars by default) which often indicate
scraping artifacts from the willwulfken/MidJourney-Styles-and-Keywords-Reference
import (HTML tags, XML attributes, pipe separators, etc.).

Usage:
  python3 tools/pws-clean-short-terms.py                          # dry-run report only
  python3 tools/pws-clean-short-terms.py --apply                  # fix all detected issues
  python3 tools/pws-clean-short-terms.py --max-len 30             # custom threshold
  python3 tools/pws-clean-short-terms.py --file keywords/categories/styles.json  # single file
  python3 tools/pws-clean-short-terms.py --fix-crudely            # strip after first separator
  python3 tools/pws-clean-short-terms.py --report output/report.json  # save JSON report

Types of issues detected:
  - HTML/XML fragments: `<Img Src=...`, `Width="256" />`
  - Pipe-separated scrapes: `term | extra info`
  - Repeated mj_v5_ ID prefix in term field
  - "rendered as a ..." description strings
  - Generic terms > 40 characters
"""

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class LongTermIssue:
    file: str
    keyword_id: str
    current_term: str
    term_length: int
    issue_type: str
    suggested_fix: Optional[str] = None
    action_taken: Optional[str] = None


def is_artifact_term(term: str) -> tuple[bool, str]:
    """Detect if a term is likely a scraping artifact."""
    # HTML/XML fragments
    if any(marker in term for marker in ['<Img Src=', 'Width="', 'Width =', '/>', '</', '<svg']):
        return True, "html_artifact"
    # Pipe separator (typical web scrape pattern)
    if ' | ' in term:
        return True, "pipe_separator"
    # Repeated mj_v5_ prefix (copy-paste error from ID)
    if re.search(r'mj_v5_.*mj_v5_', term):
        return True, "repeated_mj_prefix"
    # "rendered as a ..." strings >40 chars (MJ reference scraping artifact)
    if term.lower().startswith(('rendered as a ', 'rendered as an ')) and len(term) > 40:
        return True, "description_string"
    # "in the ... aesthetic — ..." description pattern >50 chars (most are fine prompts)
    if re.match(r'in the \S+ aesthetic', term, re.IGNORECASE) and len(term) > 50:
        return True, "aesthetic_description"
    return False, ""


def clean_term(term: str, issue_type: str) -> str:
    """Generate a cleaned version of the term."""
    if issue_type == "html_artifact":
        # Extract the actual term before HTML fragments
        # e.g. "Crystalcore\" Width=\"256\" /> | <Img Src=..."
        match = re.match(r'^([^\s"<]+(?:\s+[^\s"<]+)*)', term)
        if match:
            return match.group(1).strip()
        # Fallback: take first word
        words = term.replace('"', '').replace('\\', '').split()
        return words[0] if words else term[:20]
    elif issue_type == "pipe_separator":
        return term.split(' | ')[0].strip()
    elif issue_type == "repeated_mj_prefix":
        # Keep only the first meaningful portion
        return term.split(' mj_v5_')[0].strip()
    elif issue_type == "description_string":
        return term[:40].strip()
    elif issue_type == "aesthetic_description":
        # Extract just the aesthetic name
        match = re.match(r'in the (\S+) aesthetic', term, re.IGNORECASE)
        if match:
            aesthetic = match.group(1).lower().replace('-', ' ')
            return f"in the {aesthetic} aesthetic"
        return term[:40].strip()
    return term[:40].strip()


def scan_keywords(max_len: int = 40, file_path: Optional[str] = None,
                  include_long: bool = False) -> list[LongTermIssue]:
    """Scan all keywords for long or artifact terms.
    
    By default, only detects actual artifacts (HTML, pipe separators, repeated prefixes).
    Set include_long=True to also report terms exceeding max_len (these may be intentional
    verbose descriptions from @nodaro/prompts video prompt imports).
    """
    issues = []
    search_paths = [file_path] if file_path else glob.glob("keywords/categories/*.json")

    for fp in sorted(search_paths):
        data = json.load(open(fp))
        if not isinstance(data, list):
            data = [data]

        for item in data:
            term = item.get("term", "")
            if not term:
                continue

            term_len = len(term)

            # Check for known artifact patterns first
            is_art, art_type = is_artifact_term(term)
            if is_art:
                suggested = clean_term(term, art_type)
                issues.append(LongTermIssue(
                    file=os.path.relpath(fp),
                    keyword_id=item.get("id", "?"),
                    current_term=term[:80],
                    term_length=term_len,
                    issue_type=art_type,
                    suggested_fix=suggested
                ))
            elif include_long and term_len > max_len:
                # Generic long term — may be intentional for video prompts
                suggested = term[:max_len].strip()
                issues.append(LongTermIssue(
                    file=os.path.relpath(fp),
                    keyword_id=item.get("id", "?"),
                    current_term=term[:80],
                    term_length=term_len,
                    issue_type="exceeds_max_length",
                    suggested_fix=suggested
                ))

    return issues


def report_issues(issues: list[LongTermIssue]):
    """Print a formatted report of all issues."""
    if not issues:
        print("✅ No long/corrupted terms found.")
        return

    print(f"\n{'=' * 70}")
    print(f"  Long/Corrupted Term Report — {len(issues)} issue(s) found")
    print(f"{'=' * 70}")

    # Group by issue type
    by_type = {}
    for issue in issues:
        by_type.setdefault(issue.issue_type, []).append(issue)

    for issue_type, group in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f"\n  📋 {issue_type}: {len(group)} issue(s)")
        for issue in group[:10]:
            print(f"    [{issue.keyword_id}]")
            print(f"      current:  {issue.current_term}")
            if issue.suggested_fix:
                print(f"      suggest:  {issue.suggested_fix}")
        if len(group) > 10:
            print(f"    ... and {len(group)-10} more")

    # Category breakdown
    print(f"\n  📁 By category:")
    by_cat = {}
    for issue in issues:
        cat = issue.file.replace('keywords/categories/', '').replace('.json', '')
        by_cat[cat] = by_cat.get(cat, 0) + 1
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"    {cat:<18s} {count:>4d}")

    print(f"\n  💡 To fix automatically:")
    print(f"     python3 tools/pws-clean-short-terms.py --apply")


def apply_fixes(issues: list[LongTermIssue], fix_crudely: bool = False) -> int:
    """Apply fixes to keyword files. Returns number of fixes applied."""
    # Group by file
    by_file = {}
    for issue in issues:
        by_file.setdefault(issue.file, []).append(issue)

    fixes_applied = 0
    for fp, file_issues in by_file.items():
        data = json.load(open(fp))
        if not isinstance(data, list):
            data = [data]

        for item in data:
            term = item.get("term", "")
            for issue in file_issues:
                if item.get("id") == issue.keyword_id:
                    new_term = issue.suggested_fix
                    if fix_crudely:
                        new_term = term[:40].strip()
                    if new_term and new_term != term:
                        item["term"] = new_term
                        # Also update labels if they reference old term
                        old_labels = item.get("labels", [])
                        new_labels = [
                            lb for lb in old_labels
                            if lb.lower() not in term.lower().split()
                        ]
                        new_short = new_term.lower().split()[:3]
                        for word in new_short:
                            if word not in new_labels:
                                new_labels.append(word)
                        item["labels"] = new_labels
                        fixes_applied += 1

        # Write back
        with open(fp, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

    return fixes_applied


def save_report(issues: list[LongTermIssue], output_path: str):
    """Save issues as JSON report."""
    report = {
        "version": "1.0",
        "total_issues": len(issues),
        "issues": [asdict(i) for i in issues],
        "by_type": {},
        "by_file": {}
    }
    for issue in issues:
        report["by_type"][issue.issue_type] = report["by_type"].get(issue.issue_type, 0) + 1
        report["by_file"][issue.file] = report["by_file"].get(issue.file, 0) + 1

    with open(output_path, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📄 Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect and fix long/corrupted term values in PWS keywords"
    )
    parser.add_argument("--max-len", type=int, default=40, help="Max term length for --scan-long (default: 40)")
    parser.add_argument("--apply", action="store_true", help="Apply fixes automatically")
    parser.add_argument("--fix-crudely", action="store_true", help="Truncate to 40 chars without intelligent cleaning")
    parser.add_argument("--file", type=str, help="Process a single category file")
    parser.add_argument("--report", type=str, help="Save JSON report to this path")
    parser.add_argument("--scan-long", action="store_true", help="Also scan for terms exceeding --max-len (default: only detect artifacts)")
    args = parser.parse_args()

    issues = scan_keywords(max_len=args.max_len, file_path=args.file, include_long=args.scan_long)
    report_issues(issues)

    if args.report:
        save_report(issues, args.report)

    if args.apply:
        fixes = apply_fixes(issues, fix_crudely=args.fix_crudely)
        print(f"\n✅ Applied {fixes} fix(es).")
    elif issues:
        print(f"\n⚠️  {len(issues)} issue(s) detected. Use --apply to fix.")


if __name__ == "__main__":
    main()
