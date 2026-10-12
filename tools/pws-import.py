#!/usr/bin/env python3
"""pws-import.py — Prompt Warehouse 统一导入管道入口。

子命令:
    minimax-h3   从 awesome-minimax-h3-prompts 仓库导入视频关键词
    camera-shots 从 ai-camera-shots 仓库导入镜头术语
    audit        执行字段审计（检查 _pending_review 状态）
    report       输出所有 _pending_review 的汇总报告

已弃用:
    prompts-chat 数据源已归档（tools/_archive/import-prompts-chat.py）
    shuixian     数据源已归档（tools/_archive/import-shuixian.py）

用法:
    python3 tools/pws-import.py minimax-h3 [--dry-run] [--force]
    python3 tools/pws-import.py camera-shots [--dry-run] [--force]
    python3 tools/pws-import.py audit
    python3 tools/pws-import.py report
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES_DIR = os.path.join(ROOT, 'bundles')
TEMPLATES_DIR = os.path.join(ROOT, 'templates')
SCHEMA_DIR = os.path.join(ROOT, 'schema')
KEYWORDS_DIR = os.path.join(ROOT, 'keywords')
CATEGORIES_DIR = os.path.join(KEYWORDS_DIR, 'categories')
META_FILE = os.path.join(KEYWORDS_DIR, '_meta.json')
PENDING_FILE = os.path.join(CATEGORIES_DIR, '_pending_review.json')

# 已归档的数据源（不再活跃）
ARCHIVED_SOURCES = {
    'prompts-chat': 'tools/_archive/import-prompts-chat.py',
    'shuixian': 'tools/_archive/import-shuixian.py',
}


def check_version(source_name: str) -> tuple:
    """检查上游数据源的版本信息。

    返回 (current_version, last_imported_version)。
    对于 Git 仓库，通过 git log 获取最新 commit hash。
    """
    source_configs = {
        'minimax-h3': {
            'repo': 'BeatAPI/awesome-minimax-h3-prompts',
            'local_dir': '/tmp/awesome-minimax-h3-prompts',
        },
        'camera-shots': {
            'repo': 'joost/ai-camera-shots',
            'local_dir': '/tmp/ai-camera-shots',
        },
    }

    config = source_configs.get(source_name)
    if not config:
        return None, None

    # 读取 _meta.json 中的上次导入版本
    try:
        with open(META_FILE, 'r') as f:
            meta = json.load(f)
        last_version = None
        imports = meta.get('imports', {})
        if isinstance(imports, dict):
            last_version = imports.get(source_name, {}).get('last_commit', None)
        elif isinstance(imports, list):
            for imp in imports:
                if imp.get('source') == source_name:
                    last_version = imp.get('last_commit', None)
                    break
    except (FileNotFoundError, json.JSONDecodeError):
        last_version = None

    # 获取当前上游最新版本（commit hash）
    current_commit = None
    local_dir = config.get('local_dir')

    if local_dir and os.path.isdir(local_dir):
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=local_dir, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                current_commit = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return current_commit, last_version


def run_import(source_name: str, dry_run: bool = False, force: bool = False):
    """执行指定数据源的导入。"""
    scripts = {
        'minimax-h3': 'tools/import-minimax-h3.py',
        'camera-shots': 'tools/import-camera-shots.py',
    }

    script_path = os.path.join(ROOT, scripts.get(source_name))
    if not os.path.exists(script_path):
        print(f"ERROR: 导入脚本不存在: {script_path}")
        sys.exit(1)

    # 版本检查
    current_commit, last_commit = check_version(source_name)

    if not force and last_commit and current_commit == last_commit:
        print(f"[skip] {source_name}: 版本未更新 (commit={current_commit})")
        print("  如需强制导入，使用 --force 参数。")
        return

    if current_commit and not force:
        print(f"[check] {source_name}: 新版本 commit={current_commit[:8]}")
        print(f"         上次导入 commit={last_commit[:8] if last_commit else 'N/A'}")

    # 执行导入脚本
    cmd = [sys.executable, script_path]
    if dry_run:
        cmd.append('--dry-run')

    print(f"\n[import] 执行 {source_name} 导入...")
    result = subprocess.run(cmd, cwd=ROOT)

    if result.returncode == 0:
        print(f"[ok] {source_name} 导入完成。")
    else:
        print(f"[error] {source_name} 导入失败 (exit code {result.returncode})")
        sys.exit(result.returncode)


def run_audit(args=None):
    """执行字段审计：检查 _pending_review 状态。"""
    if not os.path.exists(PENDING_FILE):
        print("[audit] _pending_review.json 不存在（空文件）。")
        return

    with open(PENDING_FILE, 'r') as f:
        pending = json.load(f)

    entries = pending if isinstance(pending, list) else pending.get('entries', [])
    print(f"[audit] _pending_review.json: {len(entries)} 条待审核")

    if not entries:
        print("  所有数据已入库。")
        return

    # 按分类统计
    from collections import Counter
    cat_counts = Counter()
    for e in entries:
        cat = e.get('category', 'unknown')
        cat_counts[cat] += 1

    print(f"\n按分类统计:")
    for cat in sorted(cat_counts.keys()):
        print(f"  {cat}: {cat_counts[cat]} 条")

    # 检查是否有 term_zh 缺失
    missing_zh = sum(1 for e in entries if not e.get('term_zh'))
    print(f"\n缺少 term_zh: {missing_zh}/{len(entries)}")


def run_report(args=None):
    """输出所有 _pending_review 的汇总报告。"""
    if not os.path.exists(PENDING_FILE):
        print("[report] _pending_review.json 不存在（空文件）。")
        return

    with open(PENDING_FILE, 'r') as f:
        pending = json.load(f)

    entries = pending if isinstance(pending, list) else pending.get('entries', [])

    print(f"{'=' * 70}")
    print(f"  _pending_review 汇总报告")
    print(f"{'=' * 70}")
    print(f"总待审核: {len(entries)}")

    if not entries:
        print("\n没有待审核的条目。")
        return

    from collections import Counter
    cat_counts = Counter()
    source_counts = Counter()
    missing_zh = 0

    for e in entries:
        cat_counts[e.get('category', 'unknown')] += 1
        source_counts[e.get('source', 'manual')] += 1
        if not e.get('term_zh'):
            missing_zh += 1

    print(f"\n按分类:")
    for cat in sorted(cat_counts.keys()):
        print(f"  {cat}: {cat_counts[cat]}")

    print(f"\n按来源:")
    for src in sorted(source_counts.keys()):
        print(f"  {src}: {source_counts[src]}")

    print(f"\n缺少 term_zh: {missing_zh}/{len(entries)}")

    # 列出前 20 条
    print(f"\n前 20 条待审核:")
    for e in entries[:20]:
        eid = e.get('id', 'N/A')
        term = e.get('term', '')[:50]
        has_zh = "✓" if e.get('term_zh') else "✗"
        print(f"  [{has_zh}] {eid}: \"{term}\"")

    if len(entries) > 20:
        print(f"  ... 还有 {len(entries) - 20} 条未列出")


def main():
    parser = argparse.ArgumentParser(
        prog='pws-import',
        description='Prompt Warehouse 统一导入管道入口',
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 已弃用的源
    for src, archive_path in ARCHIVED_SOURCES.items():
        sub = subparsers.add_parser(src, help=f'已弃用: 数据源已归档到 {archive_path}')
        sub.set_defaults(func=lambda args: print(
            f"[deprecated] {src} 数据源已归档至 tools/_archive/{archive_path.split('/')[-1]}。"
        ))

    # 活跃源
    for src in ['minimax-h3', 'camera-shots']:
        sub = subparsers.add_parser(src, help=f'从 {src} 导入视频关键词')
        sub.add_argument('--dry-run', action='store_true', help='仅检查，不写入')
        sub.add_argument('--force', action='store_true', help='强制导入，跳过版本检查')
        sub.set_defaults(func=lambda args: run_import(src, args.dry_run, args.force))

    # 审计
    sub = subparsers.add_parser('audit', help='执行字段审计')
    sub.set_defaults(func=run_audit)

    # 报告
    sub = subparsers.add_parser('report', help='输出 _pending_review 汇总报告')
    sub.set_defaults(func=run_report)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
