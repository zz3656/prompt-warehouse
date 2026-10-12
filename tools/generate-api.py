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
    """全局统计（含 relation / compatibility）"""
    meta = json.load(open(REPO / "keywords" / "_meta.json", encoding="utf-8"))

    total = 0
    categories = {}
    by_compat = {}
    canonical_count = 0
    variant_count = 0
    alias_count = 0
    rel_groups = set()

    for f in glob.glob(str(REPO / "keywords" / "categories" / "*.json")):
        slug = Path(f).stem
        data = json.load(open(f, encoding="utf-8"))
        categories[slug] = len(data)
        total += len(data)

        for kw in data:
            # compatibility 统计
            compat = kw.get("compatibility") or ["_universal"]
            for c in compat:
                by_compat[c] = by_compat.get(c, 0) + 1

            # relation 统计
            if kw.get("alias_of"):
                alias_count += 1
            role = kw.get("relation_role")
            if role == "canonical":
                canonical_count += 1
            elif role == "variant":
                variant_count += 1
            if kw.get("relation_group"):
                rel_groups.add(kw["relation_group"])

    wf_count = sum(1 for f in glob.glob(str(REPO / "workflows" / "*.json")) if "_meta" not in f)

    # 批次 7：score 分布 + missing_term_zh
    buckets = {"<0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, ">=0.9": 0}
    missing_zh = 0
    for f in glob.glob(str(REPO / "keywords" / "categories" / "*.json")):
        data = json.load(open(f, encoding="utf-8"))
        if isinstance(data, list):
            for kw in data:
                s = kw.get("score", 0)
                if s is None:
                    buckets["<0.5"] += 1
                elif s < 0.5:
                    buckets["<0.5"] += 1
                elif s < 0.7:
                    buckets["0.5-0.7"] += 1
                elif s < 0.9:
                    buckets["0.7-0.9"] += 1
                else:
                    buckets[">=0.9"] += 1
                if not kw.get("term_zh"):
                    missing_zh += 1

    stats = {
        "version": meta.get("version", "unknown"),
        "total_keywords": total,
        "total_categories": len(categories),
        "total_workflows": wf_count,
        "by_category": dict(sorted(categories.items(), key=lambda x: -x[1])),
        "by_compatibility": dict(sorted(by_compat.items(), key=lambda x: -x[1])),
        "relation": {
            "canonical": canonical_count,
            "variant": variant_count,
            "alias_of": alias_count,
            "relation_group": len(rel_groups)
        },
        "by_score_bucket": buckets,
        "missing_term_zh": missing_zh,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    # 批次 8：统计 workflow 引用的 template_id 中缺失的
    tpl_ids = set()
    for f in glob.glob(str(REPO / "templates" / "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if isinstance(d, list):
                for t in d:
                    if t.get("id"):
                        tpl_ids.add(t["id"])
            elif isinstance(d, dict) and d.get("id"):
                tpl_ids.add(d["id"])
        except Exception:
            pass
    missing_refs = []
    if (REPO / "workflows").exists():
        for f in glob.glob(str(REPO / "workflows" / "*.json")):
            if "_meta" in f:
                continue
            try:
                wf = json.load(open(f, encoding="utf-8"))
                for step in wf.get("steps", []):
                    tid = step.get("template_id")
                    if tid and tid not in tpl_ids:
                        missing_refs.append(tid)
            except Exception:
                pass

    stats["missing_template_refs"] = sorted(set(missing_refs))

    with open(API_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✅ stats.json: {total} keywords, {len(categories)} categories")
    print(f"   relation: canonical={canonical_count}, variant={variant_count}, "
          f"alias_of={alias_count}, groups={len(rel_groups)}")
    print(f"   compatibility: {len(by_compat)} models")


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


def generate_bundles():
    """生成 bundles API: 列表 + 单个 bundle。

    PanelCraft 通过以下端点读写 bundles：
      GET /api/bundles.json          — 列表（id/name/name_zh/keyword_count）
      GET /api/bundle_{safe_id}.json — 单个 bundle 完整内容（对应 bundles/:id）
    PUT/POST/DELETE 需要后端支持，静态 API 仅支持读取。
    """
    bundles_dir = REPO / "bundles"
    if not bundles_dir.exists():
        print("⚠️  bundles/ directory not found, skipping")
        return

    all_bundles = []
    for f in sorted(glob.glob(str(bundles_dir / "*.json"))):
        try:
            b = json.load(open(f, encoding="utf-8"))
            all_bundles.append(b)
        except Exception:
            pass

    # 列表端点
    bundle_list = {
        "version": "1.0",
        "total": len(all_bundles),
        "bundles": [
            {
                "id": b.get("id"),
                "name": b.get("name"),
                "name_zh": b.get("name_zh"),
                "description": b.get("description", "")[:200],
                "description_zh": b.get("description_zh", "")[:200],
                "category": b.get("category"),
                "keyword_count": len(b.get("keywords", [])),
                "template_count": len(b.get("templates", [])),
                "api_targets": b.get("api_targets", []),
                "bundle_type": b.get("bundle_type"),
            }
            for b in all_bundles
        ]
    }

    with open(API_DIR / "bundles.json", "w", encoding="utf-8") as f:
        json.dump(bundle_list, f, ensure_ascii=False, indent=2)
    print(f"✅ bundles.json: {len(all_bundles)} bundles")

    # 单个 bundle 端点（PanelCraft GET /api/bundles/:id → 文件模拟）
    for b in all_bundles:
        bid = b.get("id", "unknown")
        safe_id = bid.replace(".", "_").replace("-", "_")
        with open(API_DIR / f"bundle_{safe_id}.json", "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=2)


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
            "bundles": "api/bundles.json",
            "bundle_detail": "api/bundle_{id}.json (replace {id} with bundle id)",
            "keywords": "https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/keywords/",
            "templates": "https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/templates/"
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(API_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print("✅ index.json: API 入口")


def update_stats_with_bundles():
    """在 stats.json 中补充 total_bundles 和 total_templates。"""
    stats_path = API_DIR / "stats.json"
    if not stats_path.exists():
        return

    stats = json.load(open(stats_path, encoding="utf-8"))

    # bundles 计数
    bundles_dir = REPO / "bundles"
    if bundles_dir.exists():
        stats["total_bundles"] = len(list(glob.glob(str(bundles_dir / "*.json"))))
    else:
        stats["total_bundles"] = 0

    # templates 计数（排除 _meta 和 _legacy）
    tpl_dir = REPO / "templates"
    if tpl_dir.exists():
        stats["total_templates"] = len([
            f for f in glob.glob(str(tpl_dir / "*.json"))
            if "_meta" not in f and "_legacy" not in f
        ])
    else:
        stats["total_templates"] = 0

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✅ stats.json updated: total_bundles={stats.get('total_bundles')}, "
          f"total_templates={stats.get('total_templates')}")


def main():
    generate_stats()
    update_stats_with_bundles()  # P1: stats 补充 bundles/templates 统计
    generate_categories()
    generate_workflows()
    generate_bundles()           # P0: 新增 bundles API 生成
    generate_index_json()        # P0: index 添加 bundles 端点
    print("\n✅ API 生成完成")


if __name__ == "__main__":
    main()
