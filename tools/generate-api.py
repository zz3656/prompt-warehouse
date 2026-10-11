#!/usr/bin/env python3
"""生成静态 API 文件（JSON）—— 供 GitHub Pages 部署后 HTTP 访问。"""
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).parent.parent
API_DIR = REPO / "docs" / "api"
API_DIR.mkdir(parents=True, exist_ok=True)


def generate_stats():
    """全局统计"""
    meta = json.load(open(REPO / "keywords" / "_meta.json", encoding="utf-8"))

    total = 0
    categories = {}
    for f in glob.glob(str(REPO / "keywords" / "categories" / "*.json")):
        slug = Path(f).stem
        data = json.load(open(f, encoding="utf-8"))
        categories[slug] = len(data)
        total += len(data)

    wf_count = sum(1 for f in glob.glob(str(REPO / "workflows" / "*.json")) if "_meta" not in f)

    stats = {
        "version": meta.get("version", "unknown"),
        "total_keywords": total,
        "total_categories": len(categories),
        "total_workflows": wf_count,
        "by_category": dict(sorted(categories.items(), key=lambda x: -x[1])),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(API_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✅ stats.json: {total} keywords, {len(categories)} categories")


def generate_categories():
    """分类列表 + 中文名"""
    meta = json.load(open(REPO / "keywords" / "_meta.json", encoding="utf-8"))
    categories = meta.get("categories", [])
    categories_zh = meta.get("categories_zh", {})
    subcategories_zh = meta.get("subcategories_zh", {})

    result = {
        "version": meta.get("version"),
        "total": len(categories),
        "subcategories_zh": subcategories_zh,
        "categories": [
            {
                "slug": cat,
                "name_zh": categories_zh.get(cat, cat),
                "count": 0,
                "subcategories": []
            }
            for cat in categories
        ]
    }

    for item in result["categories"]:
        cat_file = REPO / "keywords" / "categories" / f"{item['slug']}.json"
        if cat_file.exists():
            data = json.load(open(cat_file, encoding="utf-8"))
            item["count"] = len(data)

            # 聚合子分类
            subs = {}
            for kw in data:
                sub = kw.get("subcategory")
                if sub:
                    subs[sub] = subs.get(sub, 0) + 1

            item["subcategories"] = [
                {
                    "slug": sub,
                    "name_zh": subcategories_zh.get(sub, sub),
                    "count": count
                }
                for sub, count in sorted(subs.items(), key=lambda x: -x[1])
            ]

    with open(API_DIR / "categories.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ categories.json: {len(categories)} categories")


def generate_workflows():
    """所有 workflow"""
    workflows = []
    for f in glob.glob(str(REPO / "workflows" / "*.json")):
        if "_meta" in f:
            continue
        try:
            data = json.load(open(f, encoding="utf-8"))
            workflows.append(data)
        except Exception:
            pass

    result = {
        "total": len(workflows),
        "workflows": workflows
    }

    with open(API_DIR / "workflows.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ workflows.json: {len(workflows)} workflows")


def generate_index_json():
    """API 索引（入口）"""
    index = {
        "name": "Prompt Warehouse API",
        "version": "1.0.0",
        "repo": "https://github.com/zz3656/prompt-warehouse",
        "endpoints": {
            "stats": "api/stats.json",
            "categories": "api/categories.json",
            "workflows": "api/workflows.json",
            "keywords": "https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/keywords/",
            "templates": "https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/templates/"
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(API_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print("✅ index.json: API 入口")


def main():
    generate_stats()
    generate_categories()
    generate_workflows()
    generate_index_json()
    print("\n✅ API 生成完成")


if __name__ == "__main__":
    main()
