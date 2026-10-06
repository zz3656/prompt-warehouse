#!/usr/bin/env python3
"""
pws-index — 构建全库关键词/模板索引

输出扁平化的 JSON 数组，包含所有关键词的最小化可检索字段，
适用于前端搜索、API 聚合等场景。

Usage:
  python3 tools/pws-index.py
  python3 tools/pws-index.py --output data/keywords_index.json
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone


def safe_load_json(path):
    """Load JSON file with error handling."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)


def safe_write_json(path, data):
    """Write JSON file with error handling."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as e:
        print(f"❌ Failed to write {path}: {e}")
        sys.exit(1)


def build_keyword_index():
    """Build a flat index of all keywords."""
    index = []
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        category = fp.split("/")[-1].replace(".json", "")
        data = safe_load_json(fp)
        if not isinstance(data, list):
            data = [data]

        for item in data:
            entry = {
                "id": item.get("id", ""),
                "term": item.get("term", ""),
                "term_zh": item.get("term_zh", ""),
                "category": item.get("category", ""),
                "subcategory": item.get("subcategory", ""),
                "labels": item.get("labels", []),
                "labels_zh": item.get("labels_zh", []),
                "aliases": item.get("aliases", []),
                "score": item.get("score"),
                "priority": item.get("priority"),
                "lifecycle": item.get("lifecycle"),
                "tags": item.get("tags", []),
                "source": item.get("source", ""),
            }
            index.append(entry)

    # Sort by category, then subcategory, then term
    index.sort(key=lambda x: (x["category"], x["subcategory"], x["term"].lower()))
    return index


def build_template_index():
    """Build a flat index of all templates."""
    index = []
    for fp in sorted(glob.glob("templates/*.json")):
        if "_meta" in fp or "_legacy" in fp:
            continue
        data = safe_load_json(fp)
        if isinstance(data, dict) and "variants" in data:
            entry = {
                "id": data.get("id", ""),
                "name": data.get("name", ""),
                "name_zh": data.get("name_zh", ""),
                "description": data.get("description", ""),
                "description_zh": data.get("description_zh", ""),
                "category": data.get("category", ""),
                "api_targets": data.get("api_targets", []),
                "lifecycle": data.get("lifecycle"),
                "score": data.get("score"),
                "variants": [
                    {
                        "id": v.get("id", ""),
                        "description": v.get("description", ""),
                        "description_zh": v.get("description_zh", ""),
                    }
                    for v in data.get("variants", [])
                ],
            }
            index.append(entry)
    return index


def main():
    parser = argparse.ArgumentParser(description="Build PWS flat index")
    parser.add_argument(
        "--output",
        metavar="FILE",
        default="data/pws_index.json",
        help="Output file path (default: data/pws_index.json)",
    )
    parser.add_argument(
        "--keywords-only",
        action="store_true",
        help="Output only keyword index",
    )
    parser.add_argument(
        "--templates-only",
        action="store_true",
        help="Output only template index",
    )
    args = parser.parse_args()

    try:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    except OSError as e:
        print(f"Failed to create directory for {args.output}: {e}")
        sys.exit(1)

    if not args.templates_only:
        kw_index = build_keyword_index()
        safe_write_json(
            args.output,
            {"version": 1, "type": "keywords", "count": len(kw_index), "items": kw_index},
        )
        print(f"📊 Keyword index: {len(kw_index)} entries → {args.output}")

    if not args.keywords_only:
        tp_index = build_template_index()
        out = args.output.replace("pws_index.json", "pws_templates_index.json")
        safe_write_json(
            out,
            {"version": 1, "type": "templates", "count": len(tp_index), "items": tp_index},
        )
        print(f"📝 Template index: {len(tp_index)} entries → {out}")

    if args.keywords_only and args.templates_only:
        print("Error: specify one of --keywords-only or --templates-only")
        sys.exit(1)


if __name__ == "__main__":
    main()
