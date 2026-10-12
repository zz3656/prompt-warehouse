#!/usr/bin/env python3
"""migrate-fields.py — 清理冗余字段：priority → score, tags → labels。

迁移规则：
  priority (string) → score (float):
    high      → 0.9
    medium    → 0.7  (默认值，与现有 score=0.5 不同，优先保留 priority 的意图)
    low       → 0.5
    experimental → 0.3 (数据中未出现，仍支持)

  tags (array) → labels (array):
    合并到现有 labels 数组，去重（保持原顺序）。

执行后从每个 keyword 对象中删除 priority / tags 字段。
"""

import glob
import json
import os
import sys

PRIORITY_MAP = {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.5,
    "experimental": 0.3,
}


def migrate_keyword(kw):
    """迁移单个 keyword 对象，返回是否被修改。"""
    modified = False

    # priority → score
    if "priority" in kw:
        p = kw["priority"]
        if p in PRIORITY_MAP:
            kw["score"] = PRIORITY_MAP[p]
            del kw["priority"]
            modified = True
        else:
            print(f"  WARNING: unknown priority '{p}' in {kw.get('id', 'unknown')}", file=sys.stderr)

    # tags → labels (合并去重)
    if "tags" in kw:
        tag_list = kw.pop("tags")
        existing_labels = kw.get("labels", [])
        # 合并并去重（保持 labels 原有顺序，追加新 tag）
        seen = set(existing_labels)
        for t in tag_list:
            if t not in seen:
                existing_labels.append(t)
                seen.add(t)
        kw["labels"] = existing_labels
        modified = True

    return modified


def main():
    category_files = sorted(glob.glob("keywords/categories/*.json"))
    if not category_files:
        print("ERROR: no keyword files found in keywords/categories/", file=sys.stderr)
        sys.exit(1)

    total_kws = 0
    migrated_kws = 0
    files_touched = set()

    for fpath in category_files:
        with open(fpath) as f:
            data = json.load(f)

        for kw in data:
            total_kws += 1
            if migrate_keyword(kw):
                migrated_kws += 1
                files_touched.add(fpath)

        # 写回文件（保持缩进风格）
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"Total keywords: {total_kws}")
    print(f"Migrated:       {migrated_kws}")
    print(f"Files touched:  {len(files_touched)}")


if __name__ == "__main__":
    main()
