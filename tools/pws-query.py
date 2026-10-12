#!/usr/bin/env python3
"""统一查询：按模型 / canonical / 分类过滤关键词

用法:
  python3 tools/pws-query.py --model sdxl --category composition --canonical-only --limit 5
  python3 tools/pws-query.py --model kling --limit 10
  python3 tools/pws-query.py --category quality --subcategory render-quality --output result.json
"""
import json, glob, argparse


def load_all():
    kws = []
    for f in glob.glob("keywords/categories/*.json"):
        cat = f.split("/")[-1].replace(".json", "")
        data = json.load(open(f, encoding="utf-8"))
        if isinstance(data, list):
            for kw in data:
                kw["_category_file"] = cat
                kws.append(kw)
    return kws


def filter_by_model(keywords, target_model):
    """过滤兼容指定模型的关键词。
    
    规则：compatibility 包含 target_model，或 compatibility 为空（通用）。
    """
    results = []
    for kw in keywords:
        compat = kw.get("compatibility", [])
        if not compat or target_model in compat:
            results.append(kw)
    return results


def is_canonical(kw):
    if kw.get("alias_of"):
        return False
    if kw.get("relation_role") == "variant":
        return False
    return True


def main():
    p = argparse.ArgumentParser(description="PWS unified keyword query")
    p.add_argument("--model", help="Filter by model (sdxl/midjourney/flux/kling/runway/minimax_h3)")
    p.add_argument("--category", help="Filter by category")
    p.add_argument("--subcategory", help="Filter by subcategory")
    p.add_argument("--canonical-only", action="store_true", help="Only canonical keywords")
    p.add_argument("--limit", type=int, default=20, help="Output limit")
    p.add_argument("--output", help="Output file (JSON)")
    args = p.parse_args()

    kws = load_all()
    if args.category:
        kws = [k for k in kws if k.get("category") == args.category]
    if args.subcategory:
        kws = [k for k in kws if k.get("subcategory") == args.subcategory]
    if args.canonical_only:
        kws = [k for k in kws if is_canonical(k)]
    if args.model:
        kws = [k for k in kws if not (k.get("compatibility") or []) or args.model in k["compatibility"]]

    if args.output:
        json.dump(kws, open(args.output, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"写入 {args.output}: {len(kws)} 条")
    else:
        print(f"匹配 {len(kws)} 条")
        for kw in kws[:args.limit]:
            print(f"  {kw['id']}: {kw['term']}")


if __name__ == "__main__":
    main()
