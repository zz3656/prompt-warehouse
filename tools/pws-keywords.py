#!/usr/bin/env python3
"""pws-keywords: 按模型过滤关键词"""
import json, glob, argparse
from pathlib import Path

REPO = Path(__file__).parent.parent
CATEGORIES_DIR = REPO / "keywords" / "categories"

# 全局模型列表（按 schema enum）
ALL_MODELS = ["sdxl", "midjourney", "flux", "kling", "runway", "minimax_h3"]

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

def main():
    parser = argparse.ArgumentParser(description="Filter keywords by target model")
    parser.add_argument("--model", required=True, choices=ALL_MODELS,
                        help="Target model to filter by")
    parser.add_argument("--category", default=None,
                        help="Filter by category (optional)")
    parser.add_argument("--subcategory", default=None,
                        help="Filter by subcategory (optional)")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    # 加载所有关键词
    all_keywords = []
    for f in sorted(CATEGORIES_DIR.glob("*.json")):
        cat = f.stem
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, list):
                for kw in data:
                    kw["_category"] = cat
                    all_keywords.append(kw)
    
    # 按 category 过滤
    if args.category:
        all_keywords = [kw for kw in all_keywords if kw.get("_category") == args.category]
    
    # 按 subcategory 过滤
    if args.subcategory:
        all_keywords = [kw for kw in all_keywords if kw.get("subcategory") == args.subcategory]
    
    # 按 model 过滤
    filtered = filter_by_model(all_keywords, args.model)
    
    # 输出
    result = {
        "model": args.model,
        "total_filtered": len(filtered),
        "keywords": filtered[:50]  # 前 50 条示例
    }
    
    output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)

if __name__ == "__main__":
    main()
