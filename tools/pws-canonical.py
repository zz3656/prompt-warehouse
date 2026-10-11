#!/usr/bin/env python3
"""pws-canonical: 按 canonical 去重关键词

组合器使用：只保留 canonical，过滤 variant 和 alias_of。

Usage:
  python3 tools/pws-canonical.py --limit 5
  python3 tools/pws-canonical.py --category composition --limit 10
"""
import json, glob, argparse
from pathlib import Path

REPO = Path(__file__).parent.parent
CATEGORIES_DIR = REPO / "keywords" / "categories"


def load_all():
    kws = []
    for f in sorted(CATEGORIES_DIR.glob("*.json")):
        cat = f.stem
        data = json.load(open(f, encoding="utf-8"))
        if isinstance(data, list):
            for kw in data:
                kw["_category_file"] = cat
                kws.append(kw)
    return kws


def is_canonical(kw):
    """判断是否为 canonical 条目。

    canonical = 非 alias_of、且 relation_role 不是 variant。
    """
    if kw.get("alias_of"):
        return False
    if kw.get("relation_role") == "variant":
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Filter keywords to canonical only (skip variant + alias_of)"
    )
    parser.add_argument("--category", default=None, help="Filter by category")
    parser.add_argument("--subcategory", default=None, help="Filter by subcategory")
    parser.add_argument("--limit", type=int, default=20, help="Output limit")
    parser.add_argument("--output", default=None, help="Output file (JSON)")
    args = parser.parse_args()

    kws = load_all()

    # 按 category 过滤
    if args.category:
        kws = [k for k in kws if k.get("category") == args.category]

    # 按 subcategory 过滤
    if args.subcategory:
        kws = [k for k in kws if k.get("subcategory") == args.subcategory]

    canonical = [k for k in kws if is_canonical(k)]
    filtered = len(kws) - len(canonical)

    result = {
        "total": len(kws),
        "canonical": len(canonical),
        "filtered_out": filtered,
        "keywords": canonical[:args.limit]
    }

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"输出到: {args.output}")
    else:
        print(f"总条目: {len(kws)}")
        print(f"canonical: {len(canonical)}")
        print(f"已过滤 (variant + alias_of): {filtered}")
        print()
        for kw in canonical[:args.limit]:
            print(f"  {kw['id']}: {kw['term']}")


if __name__ == "__main__":
    main()
