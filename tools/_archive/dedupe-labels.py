#!/usr/bin/env python3
"""dedupe-labels.py — 去除 labels 数组中的重复项。

一次性脚本，已执行完毕，请勿重复运行。
"""

import glob
import json
import os


def main():
    category_files = sorted(glob.glob("keywords/categories/*.json"))

    fixed_count = 0
    total_kws = 0

    for fpath in category_files:
        with open(fpath) as f:
            data = json.load(f)

        modified = False
        for kw in data:
            total_kws += 1
            labels = kw.get("labels", [])
            if len(labels) != len(set(labels)):
                # 去重，保持原顺序
                seen = set()
                deduped = []
                for l in labels:
                    if l not in seen:
                        deduped.append(l)
                        seen.add(l)
                kw["labels"] = deduped
                fixed_count += 1
                modified = True

        if modified:
            with open(fpath, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

    print(f"Total keywords: {total_kws}")
    print(f"Keywords with duplicate labels fixed: {fixed_count}")


if __name__ == "__main__":
    main()
