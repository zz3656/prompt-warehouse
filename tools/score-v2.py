#!/usr/bin/env python3
"""score-v2.py — 为全量关键词计算 score_v2（基于描述具体性、可复用性、模型兼容性）。

用法:
    python3 tools/score-v2.py [--dry-run] [--output FILE]

选项:
    --dry-run   只输出统计，不写入文件
    --output F  指定输出 JSON 文件（默认: keywords/_score_v2.json）
"""

import json
import os
import sys
import glob
from collections import defaultdict


# ── 分类可复用性评分表 ──────────────────────────────────────────────
# 通用型分类（可搭配多种场景）→ 高分；专用型（仅限特定场景）→ 低分
CATEGORY_REUSABILITY = {
    # 高可复用性：跨场景通用
    'quality': 0.95,
    'lighting': 0.90,
    'color-look': 0.85,
    'atmosphere': 0.80,
    'composition': 0.85,

    # 中等可复用性：适用于部分场景
    'scene': 0.75,
    'transitions': 0.80,
    'temporal': 0.75,
    'shot-language': 0.80,
    'panel': 0.75,

    # 较低可复用性：偏向特定类型
    'character': 0.65,
    'clothing': 0.60,
    'styles': 0.55,
    'era': 0.60,

    # 低可复用性：专用分类
    'action-fx': 0.55,
    'held-prop': 0.45,
    'material': 0.50,
    'photographer': 0.40,
    'negative': 0.50,
    'character-fx': 0.50,
}


def word_count(term: str) -> int:
    """计算 term 的词数（按空格分割）。"""
    if not term or not term.strip():
        return 0
    return len(term.split())


def specificity_score(term: str) -> float:
    """描述具体性（0-1）：基于 term 的词数。

    规则:
      0 词  → 0.3  (空/缺失)
      1 词  → 0.4  (单关键词，如 "hair")
      2 词  → 0.6  (双关键词，如 "blonde hair")
      3 词  → 0.8  (三关键词，如 "platinum blonde hair")
      4+ 词 → 0.9  (详细短语，如 "cinematic wide shot")
    """
    wc = word_count(term)
    if wc == 0:
        return 0.3
    elif wc == 1:
        return 0.4
    elif wc == 2:
        return 0.6
    elif wc == 3:
        return 0.8
    else:
        return 0.9


def reusability_score(category: str) -> float:
    """可复用性（0-1）：基于分类的跨场景适用潜力。"""
    return CATEGORY_REUSABILITY.get(category, 0.65)


def compatibility_score(compat_list: list) -> float:
    """模型兼容性（0-1）：基于 compatibility 数组长度。

    规则:
      0 个模型 → 0.2  (无兼容模型，孤立关键词)
      1 个模型 → 0.3
      2 个模型 → 0.5
      3 个模型 → 0.6
      5 个模型 → 0.8
      6 个模型 → 1.0  (全兼容)
    """
    n = len(compat_list) if compat_list else 0
    if n == 0:
        return 0.2
    elif n == 1:
        return 0.3
    elif n == 2:
        return 0.5
    elif n == 3:
        return 0.6
    elif n == 5:
        return 0.8
    elif n >= 6:
        return 1.0
    else:
        # 4 个模型（理论上不存在，但兜底）
        return 0.7


def compute_score_v2(entry: dict) -> float:
    """计算单个关键词的 score_v2。

    公式: score_v2 = 0.4 * specificity + 0.3 * reusability + 0.3 * compatibility
    """
    term = entry.get('term', '')
    category = entry.get('category', 'uncategorized')
    compat = entry.get('compatibility', [])

    s_spec = specificity_score(term)
    s_reuse = reusability_score(category)
    s_compat = compatibility_score(compat)

    score_v2 = 0.4 * s_spec + 0.3 * s_reuse + 0.3 * s_compat
    return round(score_v2, 4)


def process_category(filepath: str) -> tuple:
    """处理单个分类文件，返回 (entries, modified_count)。"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    is_list = isinstance(data, list)
    entries = data if is_list else data.get('entries', [data])

    modified_count = 0
    for entry in entries:
        old_score_v2 = entry.get('score_v2')
        new_score_v2 = compute_score_v2(entry)

        # 始终写入 score_v2（第一次运行或值变化时）
        if old_score_v2 is None or abs(old_score_v2 - new_score_v2) > 0.0001:
            entry['score_v2'] = new_score_v2

            # 同步更新 weight 字段（用于排序）
            if 'weight' in entry:
                entry['weight'] = new_score_v2

            modified_count += 1

    # 写回文件：直接写入 entries（is_list=True 时 data 和 entries 是同一对象）
    with open(filepath, 'w') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    return entries, modified_count


def main():
    dry_run = '--dry-run' in sys.argv
    output_file = 'keywords/_score_v2.json'

    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]

    categories_dir = 'keywords/categories'
    bundle_dir = 'bundles'

    all_scores_v2 = []
    all_scores_old = []
    total_entries = 0
    total_modified = 0

    # ── 处理所有关键词 ────────────────────────────────────────────
    for fpath in sorted(glob.glob(os.path.join(categories_dir, '*.json'))):
        cat_name = os.path.basename(fpath).replace('.json', '')

        data, modified_count = process_category(fpath)

        total_modified += modified_count
        is_list = isinstance(data, list)
        entries = data if is_list else data.get('entries', [data])

        for entry in entries:
            total_entries += 1
            score_v2 = entry.get('score_v2', 0)
            score_old = entry.get('score', None)

            all_scores_v2.append(score_v2)
            if score_old is not None:
                all_scores_old.append(score_old)

    # ── 统计 score_v2 分布 ────────────────────────────────────────
    buckets = {'0.00-0.30': 0, '0.30-0.50': 0, '0.50-0.70': 0,
               '0.70-0.90': 0, '0.90-1.00': 0}
    for s in all_scores_v2:
        if s <= 0.30:
            buckets['0.00-0.30'] += 1
        elif s <= 0.50:
            buckets['0.30-0.50'] += 1
        elif s <= 0.70:
            buckets['0.50-0.70'] += 1
        elif s <= 0.90:
            buckets['0.70-0.90'] += 1
        else:
            buckets['0.90-1.00'] += 1

    print(f"=== score_v2 评分统计 ===")
    print(f"总关键词数: {total_entries}")
    print(f"修改条目数: {total_modified}")
    print()

    print("score_v2 分布:")
    for bucket, count in buckets.items():
        pct = count / total_entries * 100 if total_entries else 0
        bar = '█' * int(pct / 2)
        print(f"  {bucket}: {count:>5} ({pct:5.1f}%) {bar}")

    # ── 原始 score vs score_v2 差异 ───────────────────────────────
    if all_scores_old:
        diffs = [sv2 - so for sv2, so in zip(all_scores_v2, all_scores_old)]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        max_increase = max(diffs) if diffs else 0
        max_decrease = min(diffs) if diffs else 0

        print(f"\n原始 score vs score_v2 差异:")
        print(f"  平均差异: {avg_diff:+.4f}")
        print(f"  最大提升: +{max_increase:.4f}")
        print(f"  最大下降: {max_decrease:.4f}")

    # ── 最高 / 最低分关键词 ───────────────────────────────────────
    # 需要重新遍历获取完整信息
    highest = []
    lowest = []

    for fpath in sorted(glob.glob(os.path.join(categories_dir, '*.json'))):
        cat_name = os.path.basename(fpath).replace('.json', '')
        with open(fpath, 'r') as f:
            data = json.load(f)

        is_list = isinstance(data, list)
        entries = data if is_list else data.get('entries', [data])

        for entry in entries:
            sv2 = entry.get('score_v2', 0)
            highest.append((sv2, cat_name, entry.get('id', ''),
                            entry.get('term', ''), entry.get('score', None),
                            len(entry.get('compatibility', []))))
            lowest.append((sv2, cat_name, entry.get('id', ''),
                           entry.get('term', ''), entry.get('score', None),
                           len(entry.get('compatibility', []))))

    highest.sort(key=lambda x: -x[0])
    lowest.sort(key=lambda x: x[0])

    print(f"\n最高分 10 个关键词:")
    for sv2, cat, eid, term, score_old, compat_n in highest[:10]:
        old_str = f"  (原 score: {score_old})" if score_old is not None else ""
        print(f"  {sv2:.4f}  [{cat}] {eid}: \"{term}\"{old_str}")

    print(f"\n最低分 10 个关键词:")
    for sv2, cat, eid, term, score_old, compat_n in lowest[:10]:
        old_str = f"  (原 score: {score_old})" if score_old is not None else ""
        print(f"  {sv2:.4f}  [{cat}] {eid}: \"{term}\"{old_str}")

    # ── 修复 Bundle keyword_count ─────────────────────────────────
    print(f"\n=== Bundle keyword_count 修复 ===")

    bundle_files = sorted(glob.glob(os.path.join(bundle_dir, '*.json')))
    fixed_count = 0

    for fpath in bundle_files:
        with open(fpath, 'r') as f:
            b = json.load(f)

        bid = b.get('id', os.path.basename(fpath))
        kw_list = b.get('keywords', [])
        actual_count = len(kw_list)
        declared_count = b.get('keyword_count', 0)

        if declared_count == 0 or declared_count != actual_count:
            b['keyword_count'] = actual_count
            fixed_count += 1
            print(f"  [{bid}] keyword_count: {declared_count} → {actual_count}")

            if not dry_run:
                with open(fpath, 'w') as f:
                    json.dump(b, f, ensure_ascii=False, indent=2)

    print(f"  共修复 {fixed_count}/{len(bundle_files)} 个 Bundle")

    # ── 写入 score_v2 汇总文件（非 dry-run）───────────────────────
    if not dry_run:
        score_summary = {
            'total_entries': total_entries,
            'modified_count': total_modified,
            'distribution': buckets,
        }

        # 按分类统计 score_v2 分布
        cat_stats = defaultdict(lambda: {'count': 0, 'scores': []})
        for fpath in sorted(glob.glob(os.path.join(categories_dir, '*.json'))):
            cat_name = os.path.basename(fpath).replace('.json', '')
            with open(fpath, 'r') as f:
                data = json.load(f)

            is_list = isinstance(data, list)
            entries = data if is_list else data.get('entries', [data])

            for entry in entries:
                cat_stats[cat_name]['count'] += 1
                cat_stats[cat_name]['scores'].append(entry.get('score_v2', 0))

        for cat in cat_stats:
            scores = cat_stats[cat]['scores']
            cat_stats[cat]['avg'] = round(sum(scores) / len(scores), 4) if scores else 0
            cat_stats[cat]['min'] = min(scores) if scores else 0
            cat_stats[cat]['max'] = max(scores) if scores else 0

        # 清理 scores 数组（太大，只保留统计）
        for cat in cat_stats:
            del cat_stats[cat]['scores']

        score_summary['by_category'] = dict(sorted(cat_stats.items()))

        with open(output_file, 'w') as f:
            json.dump(score_summary, f, ensure_ascii=False, indent=2)

        print(f"\nscore_v2 汇总已写入: {output_file}")

    if dry_run:
        print("\n[DRY RUN] 未写入任何文件。")


if __name__ == '__main__':
    main()
