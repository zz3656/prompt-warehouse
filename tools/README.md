# PWS 工具集

Prompt Warehouse 的命令行工具，用于关键词管理和去重。

## 工具列表

### `pws-dedup.py` — 去重工具

在添加新关键词/模板前运行，检测重复内容。

```bash
# 检查新文件与现有分类的冲突
python3 tools/pws-dedup.py --check keywords/categories/quality.json --new new_batch.json

# 扫描全部类别
python3 tools/pws-dedup.py --scan-all --new new_batch.json

# 检查单个文件内部的重复
python3 tools/pws-dedup.py --dedup-only keywords/categories/quality.json

# JSON 格式输出（适合 CI/CD 集成）
python3 tools/pws-dedup.py --dedup-only keywords/categories/quality.json --format-report

# 自动合并 term_zh 到已有条目
python3 tools/pws-dedup.py --scan-all --new new_batch.json --auto-merge
```

### `pws-translate.py` — 批量翻译工具

为关键词和模板批量补充中文翻译字段。

```bash
# 预览翻译结果（不写入）
python3 tools/pws-translate.py --translate-all --dry-run

# 生成翻译草稿供人工审查
python3 tools/pws-translate.py --generate-draft output/draft.json

# 执行批量自动翻译
python3 tools/pws-translate.py --translate-all

# 翻译单个文件
python3 tools/pws-translate.py --file keywords/categories/quality.json

# 交互式翻译（逐个确认）
python3 tools/pws-translate.py --interactive
```

## 快速开始

```bash
# 1. 添加新关键词前的标准流程
python3 tools/pws-dedup.py --scan-all --new my_new_keywords.json
# → 确认无冲突后，手动合并文件

# 2. 批量补充翻译
python3 tools/pws-translate.py --translate-all

# 3. 检查覆盖率
python3 -c "
import json, glob
total = zh = 0
for f in glob.glob('keywords/categories/*.json'):
    for item in json.load(open(f)):
        total += 1
        if item.get('term_zh'): zh += 1
print(f'term_zh: {zh}/{total} ({zh/total*100:.1f}%)')
"
```

## 文件结构

```
tools/
├── pws-dedup.py          # 去重工具
├── pws-translate.py      # 批量翻译工具
├── README.md             # 本文件
└── _translations.jsonl   # 翻译索引（由 pws-translate.py 自动生成）
```
