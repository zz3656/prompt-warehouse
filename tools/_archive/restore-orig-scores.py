#!/usr/bin/env python3
"""restore-orig-scores.py — 恢复 priority 迁移时覆盖的原始 score 值。

从 HEAD~1 (commit 06e2aa2) 提取原始 score，覆盖当前被 priority 映射写入的值。
只恢复有原始 score 的条目；没有原始 score 的条目（即之前无 score 字段）
则保留迁移后的值。

一次性脚本，已执行完毕，请勿重复运行。
"""

import glob
import json
import os
import subprocess
import sys


def main():
    repo_dir = "/Users/ceasar/Documents/GitHub/prompt-warehouse"
    os.chdir(repo_dir)

    # 从 HEAD~1 提取原始 score 映射
    category_files = sorted(glob.glob("keywords/categories/*.json"))
    if not category_files:
        print("ERROR: no keyword files found", file=sys.stderr)
        sys.exit(1)

    orig_scores = {}  # id -> original score
    for fpath in category_files:
        cat_name = os.path.basename(fpath).replace(".json", "")
        result = subprocess.run(
            ["git", "show", f"HEAD~1:keywords/categories/{cat_name}.json"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"WARNING: could not read {cat_name} from HEAD~1", file=sys.stderr)
            continue
        data = json.loads(result.stdout)
        for kw in data:
            if "score" in kw:
                orig_scores[kw["id"]] = kw["score"]

    print(f"Original scored keywords from HEAD~1: {len(orig_scores)}")

    # 对比当前，恢复被覆盖的 score
    restored_count = 0
    unchanged_count = 0

    for fpath in category_files:
        with open(fpath) as f:
            data = json.load(f)

        modified = False
        for kw in data:
            orig = orig_scores.get(kw["id"])
            if orig is not None and "score" in kw:
                if kw["score"] != orig:
                    old_score = kw["score"]
                    kw["score"] = orig
                    restored_count += 1
                    modified = True
                else:
                    unchanged_count += 1

        if modified:
            with open(fpath, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

    print(f"\nRestored:  {restored_count}")
    print(f"Unchanged (score matched): {unchanged_count}")

    # 统计恢复后的 score 分布
    all_scores = {}
    for fpath in category_files:
        with open(fpath) as f:
            data = json.load(f)
        for kw in data:
            if "score" in kw:
                s = round(kw["score"], 2)
                all_scores[s] = all_scores.get(s, 0) + 1

    print(f"\nScore distribution after restore:")
    for s in sorted(all_scores.keys()):
        print(f"  {s}: {all_scores[s]}")


if __name__ == "__main__":
    main()
