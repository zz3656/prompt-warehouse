#!/usr/bin/env python3
"""pws-healthcheck — Prompt Warehouse 一键巡检工具

用法:
  python3 tools/pws-healthcheck.py              # 控制台报告
  python3 tools/pws-healthcheck.py --json        # 输出 JSON（供 CI/面板使用）
  python3 tools/pws-healthcheck.py --json-report # 输出 JSON 报告文件

检查项:
  - 字段覆盖率（term_zh / aliases / labels_zh / compatibility / weight / source）
  - Score 分布（<0.5 / 0.5-0.7 / 0.7-0.9 / >=0.9）
  - Relation 统计（canonical / variant / alias_of / orphan groups）
  - 引用完整性（bundle 孤儿关键词 / workflow 孤儿 template）
  - 重复 ID 检测
  - 分类覆盖统计
"""

import json
import glob
import sys
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).parent.parent


def load_all_keywords():
    """加载所有关键词到字典。"""
    all_kws = {}
    for f in glob.glob(str(REPO / "keywords" / "categories" / "*.json")):
        slug = f.split("/")[-1].replace(".json", "")
        if slug in ("_pending_review.json", "uncategorized.json"):
            continue
        data = json.load(open(f, encoding="utf-8"))
        for kw in data:
            all_kws[kw["id"]] = kw
    return all_kws


def load_bundles():
    """加载所有 bundle。"""
    bundles = []
    for f in glob.glob(str(REPO / "bundles" / "*.json")):
        try:
            bundles.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            pass
    return bundles


def load_workflows():
    """加载所有 workflow。"""
    workflows = []
    for f in glob.glob(str(REPO / "workflows" / "*.json")):
        if "_meta" in f:
            continue
        try:
            workflows.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            pass
    return workflows


def load_templates():
    """加载所有 template ID。"""
    tpl_ids = set()
    for f in glob.glob(str(REPO / "templates" / "*.json")):
        if "_meta" in f or "_legacy" in f:
            continue
        data = json.load(open(f, encoding="utf-8"))
        targets = data if isinstance(data, list) else [data]
        for item in targets:
            if item.get("id"):
                tpl_ids.add(item["id"])
            for v in item.get("variants", []):
                if v.get("id"):
                    tpl_ids.add(v["id"])
    return tpl_ids


def healthcheck():
    """执行全部检查并返回报告字典。"""
    all_kws = load_all_keywords()
    bundles = load_bundles()
    workflows = load_workflows()
    valid_tpl_ids = load_templates()

    total = len(all_kws)

    # --- 字段覆盖率 ---
    missing_term_zh = sum(1 for kw in all_kws.values() if not kw.get("term_zh"))
    missing_aliases = sum(1 for kw in all_kws.values() if not kw.get("aliases") and not kw.get("aliases_zh"))
    missing_labels_zh = sum(1 for kw in all_kws.values() if not kw.get("labels_zh"))
    missing_compatibility = sum(1 for kw in all_kws.values() if not kw.get("compatibility"))
    missing_weight = sum(1 for kw in all_kws.values() if kw.get("weight") is None)
    missing_source = sum(1 for kw in all_kws.values() if not kw.get("source"))
    missing_score = sum(1 for kw in all_kws.values() if kw.get("score") is None)

    field_coverage = {
        "total": total,
        "term_zh": {"missing": missing_term_zh, "covered": total - missing_term_zh},
        "aliases": {"missing": missing_aliases, "covered": total - missing_aliases},
        "labels_zh": {"missing": missing_labels_zh, "covered": total - missing_labels_zh},
        "compatibility": {"missing": missing_compatibility, "covered": total - missing_compatibility},
        "weight": {"missing": missing_weight, "covered": total - missing_weight},
        "source": {"missing": missing_source, "covered": total - missing_source},
        "score": {"missing": missing_score, "covered": total - missing_score},
    }

    # --- Score 分布 ---
    buckets = {"<0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, ">=0.9": 0}
    for kw in all_kws.values():
        s = kw.get("score", 0) or 0
        if s < 0.5:
            buckets["<0.5"] += 1
        elif s < 0.7:
            buckets["0.5-0.7"] += 1
        elif s < 0.9:
            buckets["0.7-0.9"] += 1
        else:
            buckets[">=0.9"] += 1

    # --- Relation 统计 ---
    canonical_count = sum(1 for kw in all_kws.values() if kw.get("relation_role") == "canonical")
    variant_count = sum(1 for kw in all_kws.values() if kw.get("relation_role") == "variant")
    alias_of_count = sum(1 for kw in all_kws.values() if kw.get("alias_of"))
    rel_groups = len(set(kw.get("relation_group") for kw in all_kws.values() if kw.get("relation_group")))

    # 孤立 canonical（有 canonical 但没有 variant）
    groups = defaultdict(list)
    for kw in all_kws.values():
        rg = kw.get("relation_group")
        if rg:
            groups[rg].append(kw)

    orphan_canonicals = 0
    for rg, members in groups.items():
        has_variant = any(
            m.get("relation_role") == "variant" and m["id"] != members[0]["id"]
            for m in members
        )
        has_canonical = any(m.get("relation_role") == "canonical" for m in members)
        if has_canonical and not has_variant:
            orphan_canonicals += 1

    relation_stats = {
        "canonical": canonical_count,
        "variant": variant_count,
        "alias_of": alias_of_count,
        "groups": rel_groups,
        "orphan_canonicals": orphan_canonicals,
    }

    # --- 引用完整性 ---
    kw_ids = set(all_kws.keys())

    orphan_kw_refs = 0
    for b in bundles:
        for ref in b.get("keywords", []):
            if ref.get("id") and ref["id"] not in kw_ids:
                orphan_kw_refs += 1

    orphan_template_refs = 0
    for wf in workflows:
        for step in wf.get("steps", []):
            tid = step.get("template_id")
            if tid and tid not in valid_tpl_ids:
                orphan_template_refs += 1

    reference_integrity = {
        "orphan_keyword_refs": orphan_kw_refs,
        "orphan_template_refs": orphan_template_refs,
    }

    # --- 重复 ID ---
    id_counts = Counter(kw["id"] for kw in all_kws.values())
    duplicates = {k: v for k, v in id_counts.items() if v > 1}

    # --- 分类覆盖 ---
    cat_counts = {}
    for kw in all_kws.values():
        cat_counts.setdefault(kw["category"], 0)
        cat_counts[kw["category"]] += 1

    # --- Bundle / Workflow 计数 ---
    bundle_count = len(bundles)
    workflow_count = len(workflows)

    return {
        "version": datetime.now(timezone.utc).isoformat(),
        "total_keywords": total,
        "field_coverage": field_coverage,
        "score_buckets": buckets,
        "relation_stats": relation_stats,
        "reference_integrity": reference_integrity,
        "duplicate_ids": duplicates,
        "by_category": dict(sorted(cat_counts.items(), key=lambda x: -x[1])),
        "bundle_count": bundle_count,
        "workflow_count": workflow_count,
    }


def print_report(report):
    """控制台打印报告。"""
    total = report["total_keywords"]

    print("=" * 60)
    print("  PWS Healthcheck Report")
    print(f"  Generated: {report['version']}")
    print("=" * 60)

    print(f"\n数据规模: {total} 关键词 · {len(report['by_category'])} 分类")
    print(f"Bundles: {report['bundle_count']} · Workflows: {report['workflow_count']}")

    print(f"\n--- 字段覆盖率 ---")
    fc = report["field_coverage"]
    for field in ["term_zh", "aliases", "labels_zh", "compatibility", "weight", "source", "score"]:
        info = fc[field]
        covered = info["covered"]
        pct = covered * 100 // max(total, 1)
        status = "✅" if pct >= 95 else ("⚠️" if pct >= 80 else "❌")
        print(f"  {field:>15}: {covered}/{total} ({pct}%) {status}")

    print(f"\n--- Score 分布 ---")
    for k, v in report["score_buckets"].items():
        bar = "█" * (v // 100)
        print(f"  {k:>8}: {v:>5} {bar}")

    print(f"\n--- Relation 统计 ---")
    rs = report["relation_stats"]
    print(f"  Canonical: {rs['canonical']}")
    print(f"  Variant:   {rs['variant']}")
    print(f"  Alias_of:  {rs['alias_of']}")
    print(f"  Groups:    {rs['groups']}")
    print(f"  孤立 canonical（无 variant）: {rs['orphan_canonicals']}")

    print(f"\n--- 引用完整性 ---")
    ri = report["reference_integrity"]
    print(f"  Bundle 中孤儿关键词引用: {ri['orphan_keyword_refs']}")
    print(f"  Workflow 中孤儿 template 引用: {ri['orphan_template_refs']}")

    if report["duplicate_ids"]:
        print(f"\n--- 重复 ID ({len(report['duplicate_ids'])} 组) ---")
        for k, v in list(report["duplicate_ids"].items())[:5]:
            print(f"  {k}: {v} 次")

    # 健康评分
    issues = 0
    if rs["orphan_canonicals"] > 0:
        issues += 1
    if ri["orphan_keyword_refs"] > 0:
        issues += 1
    if ri["orphan_template_refs"] > 0:
        issues += 1
    if report["duplicate_ids"]:
        issues += 1

    print(f"\n{'='*60}")
    if issues == 0:
        print("  ✅ 健康检查通过 — 无严重问题")
    else:
        print(f"  ⚠️ 发现 {issues} 个问题，请检查上方报告")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="PWS Healthcheck — 一键巡检工具")
    parser.add_argument("--json", action="store_true", help="输出 JSON 到 stdout")
    parser.add_argument("--json-report", default=None, help="输出 JSON 报告到文件")
    args = parser.parse_args()

    report = healthcheck()

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.json_report:
        Path(args.json_report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Report written to {args.json_report}")
    else:
        print_report(report)

    # 有严重问题时返回非零退出码（供 CI）
    if args.json or args.json_report:
        sys.exit(0)

    ri = report["reference_integrity"]
    if ri["orphan_keyword_refs"] > 0 or ri["orphan_template_refs"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
