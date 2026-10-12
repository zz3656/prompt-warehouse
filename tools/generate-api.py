

def keyword_stats(kws, detailed=False):
    total = len(kws)
    if total == 0:
        print("No keywords found.")
        return

    # Required field coverage
    fields = {
        "id": lambda x: bool(x.get("id")),
        "term": lambda x: bool(x.get("term")),
        "term_zh": lambda x: bool(x.get("term_zh")),
        "category": lambda x: bool(x.get("category")),
        "subcategory": lambda x: bool(x.get("subcategory")),
        "aliases": lambda x: bool(x.get("aliases")),
        "aliases_zh": lambda x: bool(x.get("aliases_zh")),
        "labels": lambda x: bool(x.get("labels")),
        "labels_zh": lambda x: bool(x.get("labels_zh")),
        "score": lambda x: x.get("score") is not None,
        "priority": lambda x: bool(x.get("priority")),
        "lifecycle": lambda x: bool(x.get("lifecycle")),
        "tags": lambda x: bool(x.get("tags")),
        "created_at": lambda x: bool(x.get("created_at")),
        "updated_at": lambda x: bool(x.get("updated_at")),
        "source": lambda x: bool(x.get("source")),
    }

    print("=" * 60)
    print("  PWS Keyword Statistics")
    print("=" * 60)
    print(f"\n📊 Total keywords: {total}")

    print(f"\n📝 Required field coverage:")
    for field, check in fields.items():
        if field in ("id", "term", "category", "subcategory"):
            continue  # already required by schema
        count = sum(1 for kw in kws if check(kw))
        pct = count / total * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {field:<15s} {count:>5d}/{total} ({pct:5.1f}%) {bar}")

    print(f"\n🌍 Bilingual coverage:")
    zh_only = sum(1 for kw in kws if kw.get("term_zh") and not kw.get("term"))
    en_only = sum(1 for kw in kws if kw.get("term") and not kw.get("term_zh"))
    both = sum(1 for kw in kws if kw.get("term") and kw.get("term_zh"))
    neither = sum(1 for kw in kws if not kw.get("term") and not kw.get("term_zh"))
    print(f"  Both en + zh: {both} ({both/total*100:.1f}%)")
    print(f"  EN only:      {en_only} ({en_only/total*100:.1f}%)")
    print(f"  ZH only:      {zh_only} ({zh_only/total*100:.1f}%)")
    print(f"  Neither:      {neither} ({neither/total*100:.1f}%)")

    print(f"\n📈 Score distribution:")
    score_bins = defaultdict(int)
    for kw in kws:
        s = kw.get("score", 0)
        if s is None:
            score_bins["null"] += 1
        elif s >= 0.9:
            score_bins["0.9-1.0"] += 1
        elif s >= 0.75:
            score_bins["0.75-0.9"] += 1
        elif s >= 0.5:
            score_bins["0.5-0.75"] += 1
        else:
            score_bins["<0.5"] += 1
    for bin_name in ["0.9-1.0", "0.75-0.9", "0.5-0.75", "<0.5", "null"]:
        if bin_name in score_bins:
            print(f"  {bin_name:<12s} {score_bins[bin_name]:>5d}")

    print(f"\n🔄 Lifecycle distribution:")
    life_counts = Counter(kw.get("lifecycle", "unknown") for kw in kws)
    for lc, count in life_counts.most_common():
        print(f"  {lc:<12s} {count:>5d} ({count/total*100:.1f}%)")

    print(f"\n📁 Category breakdown:")
    cat_counts = Counter(kw.get("category", "unknown") for kw in kws)
    for cat, count in cat_counts.most_common():
        print(f"  {cat:<18s} {count:>5d}")

    if detailed:
        print(f"\n📋 Subcategory breakdown:")
        sub_counts = Counter(
            f"{kw.get('category','?')}/{kw.get('subcategory','?')}" for kw in kws
        )
        for sub, count in sub_counts.most_common():
            print(f"  {sub:<35s} {count:>5d}")

    # Print coverage tip
    zh_pct = both / total * 100 if total > 0 else 0
    print(f"\n💡 term_zh coverage: {zh_pct:.1f}%")
    if zh_pct < 20:
        print("   Run: python3 tools/pws-translate.py --translate-all")
    elif zh_pct < 50:
        print("   Recommend: manual review of remaining untranslated keywords")

    # Translation index stats
    idx_path = os.path.join("keywords", "_translations.jsonl")
    if os.path.exists(idx_path):
        try:
            with open(idx_path, encoding="utf-8") as fh:
                entries = [json.loads(line) for line in fh if line.strip()]
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️  Could not read translation index: {e}")
            entries = []
        print(f"\n📖 Translation index: {len(entries)} entries")


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



def build_workflow_index():
    """Build a flat index of all workflows."""
    index = []
    meta_path = "workflows/_meta.json"
    if not os.path.exists(meta_path):
        print("⚠️ No workflows/_meta.json found, skipping workflow index")
        return index

    meta = safe_load_json(meta_path)
    for wf_id in meta.get("workflows", []):
        wf_file = f"workflows/{wf_id}.json"
        if not os.path.exists(wf_file):
            print(f"⚠️ {wf_file} not found, skipping")
            continue
        data = safe_load_json(wf_file)
        entry = {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "name_zh": data.get("name_zh", ""),
            "description": data.get("description", ""),
            "description_zh": data.get("description_zh", ""),
            "use_case": data.get("use_case", []),
            "api_targets": data.get("api_targets", []),
            "output_format": data.get("output_format", ""),
            "steps": [
                {
                    "order": s.get("order"),
                    "template_id": s.get("template_id", ""),
                    "required": s.get("required", False),
                    "description_zh": s.get("description_zh", ""),
                }
                for s in data.get("steps", [])
            ],
            "example_output": data.get("example_output", ""),
            "version": data.get("version", ""),
        }
        index.append(entry)
    return index



def template_stats(templates):
    if not templates:
        print("No templates found.")
        return
    print(f"\n{'=' * 60}")
    print("  PWS Template Statistics")
    print(f"{'=' * 60}")
    total = len(templates)
    print(f"\n📊 Total templates: {total}")

    zh_names = sum(1 for t in templates if t.get("name_zh"))
    zh_desc = sum(1 for t in templates if t.get("description_zh"))
    variants_total = sum(len(t.get("variants", [])) for t in templates)
    variants_zh = sum(
        1
        for t in templates
        for v in t.get("variants", [])
        if v.get("description_zh")
    )

    print(f"  name_zh:       {zh_names}/{total} ({zh_names/total*100:.1f}%)")
    print(f"  description_zh:{zh_desc}/{total} ({zh_desc/total*100:.1f}%)")
    print(f"  Variants:      {variants_total} total, {variants_zh} with zh descriptions")
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
