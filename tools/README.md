# PWS 工具集

Prompt Warehouse 的命令行工具，用于关键词管理和去重。

## 工具列表

> **归档**: `tools/archive/pws-merge-categories.py`（分类合并工具）已移至 `tools/archive/`，合并操作已完成，不再需要。

### `extend-translations*.py` — 翻译字典批量扩充

对 `pws-translate.py` 中的 `PRE_TRANSLATIONS` 字典进行批量追加。这些脚本是幂等的——重复运行不会创建重复条目（现有键会被跳过）。

```bash
python3 tools/extend-translations.py       # 基础 lighting/color/character/clothing 词汇
python3 tools/extend-translations-2.py    # 负提示词/composition/photographer 等
python3 tools/extend-translations-3.py    # 服装 / 发型 / 眼瞳 / 30+ 张倩术语
python3 tools/extend-translations-4.py    # 半色调 / 角色代词 / 常见材质
```

> 📚 每个脚本都是一个独立可运行的批次，未来需要添加新的翻译时直接编辑这些脚本、在底部增加 `EXTRA_TRANSLATIONS_N["new_term"] = "新译"` 即可。

### `pws-audit.py` — 统一数据质量审计（推荐）

一键运行所有数据质量检查，是提交前/CI 集成的首选。

```bash
python3 tools/pws-audit.py              # 完整审计报告
python3 tools/pws-audit.py --strict    # 发现警告也退出码为 1
python3 tools/pws-audit.py --quiet     # 仅输出汇总
python3 tools/pws-audit.py --report audit.json  # 保存为 JSON
```

**检查项**：JSON 语法、schema 验证、ID 模式、跨分类重复、_meta.json 一致性、字段覆盖率、评分范围、lifecycle 枚举、category 枚举、模板 schema 验证、抓取 artefacts 检测（HTML 标签、pipe 分隔符、mj_v5_ 重复前缀）。

### `pws-clean-long-terms.py` — 长 term 检测与清理

检测过长的或被破坏的 term 值，默认仅清理已知 scrape artifacts；详细长 term（来自 @nodaro/prompts）需 `--scan-long` 才会报告。

```bash
python3 tools/pws-clean-long-terms.py                  # 仅检测 artifacts (default)
python3 tools/pws-clean-long-terms.py --apply          # 自动修复 artifacts
python3 tools/pws-clean-long-terms.py --scan-long      # 也报告超过 max-len 的 term
python3 tools/pws-clean-long-terms.py --max-len 30     # 自定义阈值
python3 tools/pws-clean-long-terms.py --file keywords/categories/styles.json
python3 tools/pws-clean-long-terms.py --report report.json  # 保存 JSON 报告
```

**检测的 artifact 类型**：HTML 片段 (`<Img Src=`、`Width="`)、`|` 分隔符、重复 `mj_v5_` 前缀、"rendered as a ..." 描述串、"in the ... aesthetic — ..." 描述。

### `pws-fix-mj-artifacts.py` — MJ 抓取 artefacts 修复

专门处理 willwulfken/MidJourney-Styles-and-Keywords-Reference 导入的 HTML/IMG 痕迹。

```bash
python3 tools/pws-fix-mj-artifacts.py                # dry-run 检测
python3 tools/pws-fix-mj-artifacts.py --apply         # 自动修复
python3 tools/pws-fix-mj-artifacts.py --file keywords/categories/styles.json
python3 tools/pws-fix-mj-artifacts.py --report report.json
```

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

为关键词批量补充中文翻译字段（`term_zh`, `aliases_zh`, `labels_zh`）。

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

### `pws-index.py` — 索引生成工具

生成扁平化的关键词/模板索引，用于快速搜索和 API 聚合。

```bash
# 生成完整索引
python3 tools/pws-index.py

# 仅生成关键词索引
python3 tools/pws-index.py --keywords-only

# 指定输出路径
python3 tools/pws-index.py --output data/custom_index.json
```

### `pws-generate-labels-zh.py` — labels_zh 生成工具

为有 `term_zh` 的关键词自动生成中文搜索标签（`labels_zh`）。

```bash
# 预览生成结果
python3 tools/pws-generate-labels-zh.py --dry-run

# 应用生成结果
python3 tools/pws-generate-labels-zh.py --apply

# 处理单个文件
python3 tools/pws-generate-labels-zh.py --apply --file keywords/categories/quality.json
```

**生成策略**：
1. 从 category 获取中文分类名（如 quality → 质量）
2. 从 subcategory 获取中文子分类名
3. 从 term_zh 提取 2-4 个字符的有意义的词
4. 从 source 获取来源标签（nodaro / mj / danbooru）

> ⚠️ 仅对有 `term_zh` 的关键词生成 labels_zh（约 8%），无 term_zh 的关键词暂不生成。

### `pws-stats.py` — 统计工具

查看关键词和模板的覆盖率、分布统计。

```bash
# 基础统计
python3 tools/pws-stats.py

# 详细统计（含子分类）
python3 tools/pws-stats.py --detailed

# 单分类统计
python3 tools/pws-stats.py --category quality
```

## 快速开始

```bash
# 1. 查看当前状态
python3 tools/pws-stats.py

# 2. 添加新关键词前的标准流程
python3 tools/pws-dedup.py --scan-all --new my_new_keywords.json
# → 确认无冲突后，手动合并文件

# 3. 批量补充翻译
python3 tools/pws-translate.py --translate-all

# 4. 生成 labels_zh
python3 tools/pws-generate-labels-zh.py --dry-run
python3 tools/pws-generate-labels-zh.py --apply

# 5. 生成可搜索索引
python3 tools/pws-index.py

# 6. 检查覆盖率
python3 tools/pws-stats.py
```

## 文件结构

```
tools/
├── pws-dedup.py             # 去重工具
├── pws-translate.py         # 批量翻译工具
├── pws-generate-labels-zh.py # labels_zh 生成工具
├── pws-stats.py             # 统计工具
├── pws-index.py             # 索引生成工具
├── README.md                # 本文件
└── archive/
    └── pws-merge-categories.py  # 归档：分类合并工具（已完成）

keywords/
└── _translations.jsonl   # 翻译索引（由 pws-translate.py 自动生成）
```
