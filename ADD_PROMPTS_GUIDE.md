# 提示词补充指南（含去重机制）

> 为其他项目提供标准的中英双语提示词条目

---

## 1. 数据模型（中英双语字段）

### 关键词（Keyword）

每个关键词 **必须** 包含中文字段：

```json
{
  "id": "quality_basic_masterpiece",
  "term": "masterpiece",
  "term_zh": "杰作",
  "aliases": ["best work", "top tier"],
  "aliases_zh": ["最佳作品", "顶级"],
  "category": "quality",
  "subcategory": "basic",
  "labels": ["quality", "booster"],
  "labels_zh": ["质量", "增强"],
  "score": 0.95,
  "priority": "high",
  "lifecycle": "approved",
  "tags": ["migrated"],
  "created_at": "2026-09-27T17:25:55Z",
  "updated_at": "2026-09-29T00:00:00Z",
  "source": "h3-comic-builder",
  "usage_count": 0,
  "notes": "原始备注"
}
```

#### 中文字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `term_zh` | ✅ | 中文标准翻译（如 "masterpiece" → "杰作"） |
| `aliases_zh` | | 中文替代说法（如 "best quality" → "最高质量"） |
| `labels_zh` | | 中文搜索标签（如 ["质量", "增强"]） |

### 模板（Template）

每个模板 **必须** 包含中文字段：

```json
{
  "id": "h3.video_prompts",
  "name": "H3 Video Generation Prompts",
  "name_zh": "H3 视频生成提示词",
  "description": "Video generation prompt templates...",
  "description_zh": "针对 Minimax H3 模型优化的视频生成提示词模板……",
  "variants": [
    {
      "id": "cinematic_reveal",
      "description": "Cinematic establishing shot…",
      "description_zh": "具有戏剧性镜头运动的电影开场镜头",
      "template": "Cinematic wide shot, slow dolly forward through…"
    }
  ]
}
```

---

## 2. 新增关键词流程

### Step 1: 准备新关键词 JSON

创建一个临时文件，包含要新增的关键词：

```bash
# 示例：新增 5 个质量类关键词
cat > /tmp/new_quality.json << 'EOF'
[
  {
    "id": "quality_basic_ultra_detailed",
    "term": "ultra-detailed",
    "term_zh": "超精细",
    "category": "quality",
    "subcategory": "basic",
    "labels": ["quality", "detail"],
    "labels_zh": ["质量", "细节"],
    "score": 0.90,
    "priority": "high",
    "lifecycle": "draft",
    "tags": ["new"],
    "source": "web-research",
    "created_at": "2026-10-01T00:00:00Z"
  }
]
EOF
```

### Step 2: 运行去重检查

```bash
# 检查新关键词与现有的 quality.json 是否重复
python3 tools/pws-dedup.py --check keywords/categories/quality.json --new /tmp/new_quality.json

# 或者扫描全部类别
python3 tools/pws-dedup.py --scan-all --new /tmp/new_quality.json
```

**输出说明：**
- 🟢 `No duplicates found. Safe to add.` → 可以安全添加
- 🟡 `Similar term dupes` → 警告：相似的 term，请人工确认
- 🔴 `ID conflicts` / `Exact term dupes` → 必须处理冲突

### Step 3: 处理冲突

**ID 冲突** — 该 ID 已存在，需修改新关键词的 `id`：
```
🔴 ID CONFLICTS:
  id: quality_basic_masterpiece
    new:    masterpiece (term_zh: 杰作)
    exist:  masterpiece (file: keywords/categories/quality.json)
```
→ 新关键词应改为 `quality_basic_ultra_refined` 或其他不冲突的 ID。

**term 重复** — 该 term 已存在，检查 `term_zh` 是否一致：
```
🔴 EXACT TERM DUPLICATES:
  term: blonde hair
    new:    id=quality_new_blonde  cat=quality  term_zh=金发
    exist:  id=character_hair_blonde  cat=character  term_zh=金发
```
→ 这是正常情况（同一 term 可能在不同类别中），但需确认是否真的需要新增。

### Step 4: 合并到正确文件

确认无冲突后，将新关键词追加到对应分类文件：

```bash
python3 << 'PYEOF'
import json

# 读取现有分类文件
with open("keywords/categories/quality.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 读取新关键词
with open("/tmp/new_quality.json", "r", encoding="utf-8") as f:
    new_items = json.load(f)

# 追加
data.extend(new_items)

# 写入
with open("keywords/categories/quality.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

# 更新 _meta.json
with open("keywords/_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

meta["total_keywords"] = len([
    kw for fp in __import__('glob').glob("keywords/categories/*.json")
    for kw in json.load(open(fp))
])
meta["updated_at"] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()

with open("keywords/_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Added {len(new_items)} keywords. Total: {meta['total_keywords']}")
PYEOF
```

### Step 5: 更新分类计数

```bash
python3 << 'PYEOF'
import json, glob
total = 0
for fp in glob.glob("keywords/categories/*.json"):
    data = json.load(open(fp))
    total += len(data) if isinstance(data, list) else 1
with open("keywords/_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)
meta["total_keywords"] = total
import datetime
meta["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
with open("keywords/_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"Updated total_keywords: {total}")
PYEOF
```

---

## 3. 新增模板流程

### Step 1: 准备新模板 JSON

```json
{
  "id": "my.new_template",
  "name": "My Template",
  "name_zh": "我的模板",
  "description": "English description here",
  "description_zh": "中文描述在这里",
  "category": "text-generation",
  "subcategories": ["custom"],
  "language": "en",
  "variants": [
    {
      "id": "default",
      "description": "Default variant",
      "description_zh": "默认变体",
      "template": "Your prompt template with {{variables}}"
    }
  ],
  "created_at": "2026-10-01T00:00:00Z",
  "updated_at": "2026-10-01T00:00:00Z"
}
```

### Step 2: 运行模板去重

```bash
# 检查 ID 冲突
python3 tools/pws-dedup.py --dedup-only templates/my_new_template.json

# 检查与现有模板的 term 冲突
python3 tools/pws-dedup.py --scan-all --new templates/my_new_template.json
```

### Step 3: 添加到模板文件

将模板文件保存到 `templates/` 目录，或合并到 `_all_templates.json`。

---

## 4. 批量翻译工具

如果已有英文数据但缺少中文翻译：

```bash
# 查看会翻译哪些（不写入）
python3 tools/pws-translate.py --translate-all --dry-run

# 仅生成翻译草稿供人工审查
python3 tools/pws-translate.py --generate-draft output/draft_translations.json

# 执行批量翻译（自动 + 手动）
python3 tools/pws-translate.py --translate-all

# 指定单个文件
python3 tools/pws-translate.py --file keywords/categories/quality.json

# 交互式翻译（逐个确认）
python3 tools/pws-translate.py --interactive
```

翻译数据会自动保存在 `keywords/_translations.jsonl`，方便后续审核和修改。

---

## 5. 去重机制总结

### 检测维度

| 维度 | 检测方式 | 级别 | 处理建议 |
|------|----------|------|----------|
| ID 冲突 | exact match on `id` | 🔴 错误 | 修改新项 `id` |
| term 完全重复 | exact match on `term` | 🔴 警告 | 确认是否需要新增 |
| term 相似重复 | Levenshtein distance ≤ 2 | 🟡 提醒 | 人工审查是否合并 |
| 跨分类同名 | same term, different category | ⚠️ 信息 | 正常情况，保留记录 |

### 自动合并（`--auto-merge`）

```bash
python3 tools/pws-dedup.py --scan-all --new /tmp/new_quality.json --auto-merge
```

自动合并会将新条目中的 `term_zh`、`aliases_zh`、`labels_zh` 补充到已有条目中（仅当已有条目缺失这些字段时）。

---

## 6. ID 命名规范

格式：`{category}_{subcategory}_{slug}`

| 类别 | 前缀 | 示例 |
|------|------|------|
| 质量 | `quality_basic_` / `quality_advanced_` | `quality_basic_masterpiece` |
| 构图 | `composition_framing_` / `composition_angles_` | `composition_framing_closeup` |
| 灯光 | `lighting_natural_` / `lighting_dramatic_` | `lighting_natural_golden_hour` |
| 角色 | `character_hair_` / `character_eyes_` | `character_hair_blonde` |
| 服装 | `clothing_tops_` / `clothing_outfits_` | `clothing_tops_school_uniform` |
| 风格 | `styles_anime_` / `styles_art_` | `styles_anime_cel_shading` |
| 负面 | `negative_quality_` / `negative_anatomy_` | `negative_quality_low_res` |
| 场景 | `scene_nature_` / `scene_city_` | `scene_nature_forest` |
| 分镜 | `panel_effects_` / `panel_layout_` | `panel_effects_cinematic` |

---

## 7. 快速参考命令

```bash
# 一键检查新关键词
python3 tools/pws-dedup.py --scan-all --new new_batch.json

# 检查某个文件内部的去重
python3 tools/pws-dedup.py --dedup-only keywords/categories/quality.json

# 查看 JSON 格式报告
python3 tools/pws-dedup.py --dedup-only keywords/categories/quality.json --format-report

# 执行翻译
python3 tools/pws-translate.py --translate-all --dry-run
python3 tools/pws-translate.py --translate-all

# 统计当前覆盖率
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

---

*最后更新：2026-10-01*
