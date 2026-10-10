# 向 PWS 添加新关键词的标准流程

> 提示词仓库标准 (PWS) · 增量更新指南
>
> 本文档描述如何安全、标准化地向仓库添加新关键词。适用于所有贡献者和自动化流程。

---

## 快速开始

```bash
# 1. 生成模板（一次性）
python3 tools/pws-add-new.py template --output batch_template.json

# 2. 编辑模板，填入新关键词
# 3. 提交添加（dry-run 先预览）
python3 tools/pws-add-new.py batch batch_template.json --category <类别> --dry-run

# 4. 确认无误后正式添加
python3 tools/pws-add-new.py batch batch_template.json --category <类别>

# 5. 生成可搜索索引（如未自动完成）
python3 tools/pws-index.py
```

---

## 1. 添加单个关键词

```bash
python3 tools/pws-add-new.py single \
    --term "cinematic lighting" \
    --term_zh "电影灯光" \
    --category lighting \
    --subcategory dramatic
```

自动生成 ID：`lighting_dramatic_cinematic_lighting`

---

## 2. 批量添加

准备一个 JSON 数组文件（`new_keywords.json`）：

```json
[
  {
    "id": "quality_basic_ultra_detailed",
    "term": "ultra-detailed",
    "term_zh": "超精细细节",
    "category": "quality",
    "subcategory": "advanced",
    "labels": ["quality", "detail", "refined"],
    "labels_zh": ["质量", "细节", "精细"],
    "score": 0.90,
    "priority": "high",
    "lifecycle": "approved",
    "source": "manual",
    "tags": ["high-value"],
    "notes": "适用于角色特写镜头"
  }
]
```

然后执行：

```bash
python3 tools/pws-add-new.py batch new_keywords.json --category quality
```

### 必填字段

| 字段 | 说明 |
|------|------|
| `id` | 格式：`{category}_{subcategory}_{slug}`，全部小写 |
| `term` | 英文提示词（标准形式） |
| `category` | 必须匹配 `schema/keyword.schema.json` 中的 enum |
| `subcategory` | 该分类下的子分类名称 |

### 推荐字段

| 字段 | 说明 |
|------|------|
| `term_zh` | 中文翻译（**100% 覆盖要求**） |
| `labels` | 英文搜索标签 |
| `labels_zh` | 中文搜索标签 |
| `aliases` / `aliases_zh` | 英文/中文同义词 |
| `score` | 质量评分 0–1（默认 0.5） |
| `priority` | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | `draft` → `review` → `approved` → `deprecated` → `archived` |
| `source` | 数据来源 |
| `tags` | 用户自定义标签 |
| `notes` | 自由备注 |

---

## 3. 标准工作流

### 流程一：新增关键词

```
 1. 运行 --dry-run 预览
 2. 检查 ID 冲突警告
 3. 检查术语重复警告
 4. 检查相似术语警告
 5. 确认无误后正式提交
 6. 验证 data/pws_index.json 已更新
 7. git add + commit + push
```

### 流程二：添加新分类

如果现有 20 个分类（`schema/keyword.schema.json` 的 enum）无法满足需求：

1. 编辑 `schema/keyword.schema.json` 的 `category.enum`，添加新分类 slug
2. 在 `keywords/categories/` 下创建 `{category}.json` 文件
3. 在 `keywords/_meta.json` 中更新 `total_categories`
4. 运行 `python3 tools/pws-audit.py` 确认无报错
5. 推送前确保所有现有关键词的 `category` 仍匹配更新后的 enum

---

## 4. 分类体系参考

当前 20 个分类（`schema/keyword.schema.json` 的 enum）：

| 分类 | Slug | 当前数量 |
|------|------|----------|
| 质量 | `quality` | 131 |
| 构图 | `composition` | 467 |
| 灯光 | `lighting` | 382 |
| 角色 | `character` | 503 |
| 服装 | `clothing` | 687 |
| 风格 | `styles` | 1913 |
| 负面 | `negative` | 103 |
| 场景 | `scene` | 1078 |
| 分镜 | `panel` | 74 |
| 动作特效 | `action-fx` | 75 |
| 角色特效 | `character-fx` | 60 |
| 色彩分级 | `color-look` | 69 |
| 时代 | `era` | 33 |
| 构图（高级） | `framing` | 72 |
| 手持道具 | `held-prop` | 66 |
| 摄影师 | `photographer` | 89 |
| 材质 | `material` | 67 |
| 渲染质量 | `render-quality` | 35 |
| 时间效果 | `temporal` | 30 |
| 转场效果 | `transitions` | 81 |

> 📌 小数量分类（`temporal`: 30, `era`: 33, `render-quality`: 35, `color-look`: 69, `held-prop`: 66）是高价值补充目标。

---

## 5. 验证与测试

添加后应运行：

```bash
# 完整数据质量审计
python3 tools/pws-audit.py --strict

# 重新生成索引
python3 tools/pws-index.py

# 查看统计
python3 tools/pws-stats.py
```

所有检查应通过，`data/pws_index.json` 中的 `total` 应与实际条目数一致。

---

## 6. 更多文档

- 完整数据模型和分类体系：[STANDARD.md](STANDARD.md)
- 双语提示词补充指南：[ADD_PROMPTS_GUIDE.md](ADD_PROMPTS_GUIDE.md)
- 工具集说明：[tools/README.md](tools/README.md)
- 数据来源说明：[README.md](README.md) 的「数据来源」章节

---

*最后更新：v1.0.0 · 提示词仓库标准*
