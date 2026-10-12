# 数据质量修复方案

## 任务列表与依赖关系

```
Task 1 (D-2): angle/angles 合并 → 无前置依赖
Task 2 (P0):   补全 12 个缺失 template → 无前置依赖（但 workflow 依赖）
Task 3 (P2):   新增 compatibility 字段 → 无前置依赖
Task 4 (API-2):聚合统计端点 → 依赖 Task 1-3 的数据变更
```

---

## Task 1 (D-2): 合并 angle / angles

### 1.1 盘点结果

**angle（10 条）与 angles（14 条）无 term 冲突。**

仅 angle 独有（10 条）：
- `bird's eye view`, `dutch angle shot`, `extreme dutch angle tilt`
- `eye level shot`, `high angle shot`, `low angle shot`
- `overhead shot, looking straight down`
- `slightly downward angle, just above the eyeline`
- `wide-angle lens distortion barrel`, `worm's eye view`

仅 angles 独有（14 条）：
- `back view`, `bird's-eye view`, `dutch angle`, `fourth view`
- `front view`, `hero shot`, `looking down`, `looking up`
- `low angle view`, `side profile`, `three-quarter view`
- `top-down angle`, `viewed from above`, `worm's-eye view`

**结论：无 term 冲突，可直接合并。** angle 和 angles 语义等价（都是"角度"），angle 更简洁。

### 1.2 迁移脚本伪代码

```python
# merge_angle_angles.py
import json

META = "keywords/_meta.json"
COMP_FILE = "keywords/categories/composition.json"

with open(META) as f: meta = json.load(f)
with open(COMP_FILE) as f: data = json.load(f)

# 把 subcategory="angles" 的条目改为 "angle"
changed = 0
for kw in data:
    if kw.get("subcategory") == "angles":
        kw["subcategory"] = "angle"
        changed += 1

with open(COMP_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"迁移 {changed} 条: angles → angle")
```

预期结果：`changed = 14`（angles 的 14 条全部迁移到 angle）。

### 1.3 更新 _meta.json 和 subcategories_zh

```python
# 在 _meta.json 中：
meta["total_categories"] = 19  # 不变（angle 和 angles 属于同一分类）
# subcategories_zh 加：
meta["subcategories_zh"]["angles"] = "角度（复数）"  # 标记为已废弃
```

### 1.4 校验 SQL（Python 版）

```python
import json, glob

data = json.load(open("keywords/categories/composition.json", encoding="utf-8"))
angles_count = sum(1 for kw in data if kw.get("subcategory") == "angles")
angle_count = sum(1 for kw in data if kw.get("subcategory") == "angle")

assert angles_count == 0, f"❌ angles 仍有 {angles_count} 条残留"
assert angle_count == 24, f"❌ angle 应为 24（原 10 + 迁移 14），实际 {angle_count}"

# 全局总数不变
total = sum(len(json.load(open(f))) for f in glob.glob("keywords/categories/*.json"))
assert total == 6037, f"❌ 总数变化：{total}"

print(f"✅ 校验通过: angles=0, angle=24, 总数=6037")
```

---

## Task 2 (P0): 补全 12 个缺失 template

### 2.1 缺失 template 列表（去重后 12 个）

| # | template_id | workflow 引用次数 | 对应关键词子分类 |
|---|-------------|-------------------|-----------------|
| 1 | `action.motion` | 1 (video_storyboard) | 无（需新建） |
| 2 | `atmosphere.weather` | 1 (scene_design) | atmosphere/sky |
| 3 | `camera.movement` | 1 (video_storyboard) | 无（需新建） |
| 4 | `camera.shot_type` | 1 (video_storyboard) | 无（需新建） |
| 5 | `character.multiple_views` | 1 (character_design) | character（hair 等） |
| 6 | `character.reference_description` | 3 (comic, character, video) | character（hair/eyes/face） |
| 7 | `color.grading` | 1 (scene_design) | color-look（palette/post-process） |
| 8 | `lighting.mood` | 2 (comic, scene) | lighting/mood（已有 20 条） |
| 9 | `panel.composition` | 1 (comic) | panel（panelLayout） |
| 10 | `quality.character` | 1 (character_design) | quality/basic |
| 11 | `quality.standard` | 1 (comic) | quality（basic+technical） |
| 12 | `scene.environment` | 3 (comic, scene, video) | scene（mj_v5_objects/nature） |

### 2.2 Template JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Template",
  "description": "提示词模板（工作流步骤）",
  "type": "object",
  "required": ["id", "version", "description", "variables", "render"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*\\.[a-z][a-z0-9_]*$"
    },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "description": { "type": "string" },
    "description_zh": { "type": "string" },
    "variables": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "source"],
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "description_zh": { "type": "string" },
          "source": { "type": "string", "enum": ["keyword", "template", "static"] },
          "category": { "type": "string" },
          "subcategory": { "type": "string" },
          "required": { "type": "boolean", "default": false }
        }
      }
    },
    "render": {
      "type": "object",
      "properties": {
        "format": { "type": "string", "enum": ["comma_separated", "structured", "json"] },
        "separator": { "type": "string" },
        "order": { "type": "array", "items": { "type": "string" } }
      }
    },
    "fallback": { "type": "string" },
    "dedupe_group": { "type": "string" },
    "priority": { "type": "string", "enum": ["high", "medium", "low"] },
    "lifecycle": { "type": "string", "enum": ["active", "beta", "deprecated"] },
    "api_targets": {
      "type": "array",
      "items": { "type": "string" }
    },
    "created_at": { "type": "string" }
  }
}
```

### 2.3 完整示例：character.reference_description

```json
{
  "id": "character.reference_description",
  "version": "1.0.0",
  "description": "Generate a character reference description with consistent appearance.",
  "description_zh": "生成角色外观描述：年龄、发色、瞳色、肤色等",
  "variables": [
    {
      "name": "age",
      "description": "Character age",
      "description_zh": "年龄",
      "source": "keyword",
      "category": "character",
      "subcategory": "age",
      "required": true
    },
    {
      "name": "hair_color",
      "description": "Hair color",
      "description_zh": "发色",
      "source": "keyword",
      "category": "character",
      "subcategory": "hairColors",
      "required": true
    },
    {
      "name": "hair_style",
      "description": "Hair style and length",
      "description_zh": "发型和长度",
      "source": "keyword",
      "category": "character",
      "subcategory": "hair",
      "required": true
    },
    {
      "name": "eye_color",
      "description": "Eye color",
      "description_zh": "瞳色",
      "source": "keyword",
      "category": "character",
      "subcategory": "eyeColors",
      "required": false
    },
    {
      "name": "eye_style",
      "description": "Eye shape and expression",
      "description_zh": "眼睛形状和表情",
      "source": "keyword",
      "category": "character",
      "subcategory": "eyes",
      "required": false
    },
    {
      "name": "skin_tone",
      "description": "Skin color and texture",
      "description_zh": "肤色和质感",
      "source": "keyword",
      "category": "character",
      "subcategory": "skin",
      "required": false
    },
    {
      "name": "facial_features",
      "description": "Distinctive facial features",
      "description_zh": "面部特征",
      "source": "keyword",
      "category": "character",
      "subcategory": "face",
      "required": false
    },
    {
      "name": "expression",
      "description": "Facial expression",
      "description_zh": "表情",
      "source": "keyword",
      "category": "character",
      "subcategory": "expression",
      "required": false
    },
    {
      "name": "body_type",
      "description": "Body shape and build",
      "description_zh": "体型",
      "source": "keyword",
      "category": "character",
      "subcategory": "bodyType",
      "required": false
    }
  ],
  "render": {
    "format": "comma_separated",
    "separator": ", ",
    "order": ["age", "hair_color", "hair_style", "eye_color", "eye_style", "skin_tone", "facial_features", "expression", "body_type"]
  },
  "fallback": "young woman with long hair",
  "dedupe_group": "character",
  "priority": "high",
  "lifecycle": "active",
  "api_targets": ["SDXL", "Midjourney", "Flux"],
  "created_at": "2026-10-11"
}
```

### 2.4 完整示例：scene.environment

```json
{
  "id": "scene.environment",
  "version": "1.0.0",
  "description": "Describe a scene/environment with location, objects, and atmosphere.",
  "description_zh": "描述场景环境：地点、物体、氛围",
  "variables": [
    {
      "name": "location_type",
      "description": "Type of location",
      "description_zh": "地点类型",
      "source": "keyword",
      "category": "scene",
      "subcategory": "backdrop",
      "required": true
    },
    {
      "name": "setting_type",
      "description": "Indoor/urban/nature/fantastical",
      "description_zh": "场景类型：室内/城市/自然/奇幻",
      "source": "keyword",
      "category": "scene",
      "subcategory": ["indoor", "urban", "nature", "fantastical"],
      "required": true
    },
    {
      "name": "key_objects",
      "description": "Key objects in scene",
      "description_zh": "场景关键物体",
      "source": "keyword",
      "category": "scene",
      "subcategory": "mj_v5_objects",
      "required": true
    },
    {
      "name": "nature_elements",
      "description": "Natural elements (trees, water, rocks)",
      "description_zh": "自然元素",
      "source": "keyword",
      "category": "scene",
      "subcategory": "mj_v5_nature",
      "required": false
    },
    {
      "name": "time_of_day",
      "description": "Time period",
      "description_zh": "时间",
      "source": "keyword",
      "category": "scene",
      "subcategory": "time",
      "required": false
    },
    {
      "name": "weather_condition",
      "description": "Weather and sky",
      "description_zh": "天气和天空",
      "source": "keyword",
      "category": ["scene", "atmosphere"],
      "subcategory": ["weather", "sky"],
      "required": false
    },
    {
      "name": "interaction_elements",
      "description": "Objects and characters interacting",
      "description_zh": "互动元素",
      "source": "keyword",
      "category": "scene",
      "subcategory": "interaction",
      "required": false
    }
  ],
  "render": {
    "format": "comma_separated",
    "separator": ", ",
    "order": ["location_type", "setting_type", "key_objects", "nature_elements", "time_of_day", "weather_condition", "interaction_elements"]
  },
  "fallback": "outdoor scene with trees and buildings",
  "dedupe_group": "scene",
  "priority": "high",
  "lifecycle": "active",
  "api_targets": ["SDXL", "Midjourney", "Flux"],
  "created_at": "2026-10-11"
}
```

### 2.5 其余 10 个 template 概要

| template_id | 中文名 | 变量数 | 主要来源 |
|-------------|--------|--------|---------|
| `action.motion` | 动作描述 | 5 | 需新建关键词（现有无匹配） |
| `atmosphere.weather` | 大气效果 | 3 | atmosphere/sky + scene/weather |
| `camera.movement` | 运镜描述 | 4 | 需新建关键词（现有无匹配） |
| `camera.shot_type` | 景别描述 | 3 | 需新建关键词（现有无匹配） |
| `color.grading` | 色彩分级 | 3 | color-look（palette/post-process） |
| `panel.composition` | 分镜构图 | 4 | panel（panelLayout/comicEffects） |
| `quality.character` | 角色质量 | 3 | quality/basic + character |
| `quality.standard` | 质量标准 | 5 | quality（basic+technical） |

其中 `action.motion`, `camera.movement`, `camera.shot_type` 关键词库中无对应条目，需新建。

---

## Task 3 (P2-3): 新增 compatibility 字段

### 3.1 Field Schema

在 keyword.schema.json 中新增：

```json
{
  "compatibility": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["sdxl", "midjourney", "flux", "kling", "runway", "minimax_h3"]
    },
    "description": "适用的 AI 模型列表"
  }
}
```

### 3.2 批量打标规则

按 category/subcategory 默认值：

| category | subcategory | 默认 compatibility | 说明 |
|----------|------------|-------------------|------|
| `character` | 所有 | `["sdxl", "midjourney"]` | 角色生成主流模型 |
| `scene` | 所有 | `["sdxl", "midjourney", "flux"]` | 场景生成多模型支持 |
| `shot-language` | 所有 | `["sdxl", "midjourney", "flux"]` | 镜头语言通用 |
| `shot-language` | `camera-move` | `["kling", "runway", "minimax_h3"]` | 运镜→视频模型优先 |
| `shot-language` | `lens` | `["sdxl", "midjourney", "flux"]` | 镜头→图像模型优先 |
| `lighting` | 所有 | `["sdxl", "midjourney", "flux"]` | 灯光通用 |
| `quality` | 所有 | `["sdxl", "midjourney"]` | 质量词通用 |
| `negative` | 所有 | `["sdxl", "midjourney", "flux"]` | 负面词通用 |
| `styles` | 所有 | `["sdxl", "midjourney"]` | 风格通用 |
| `atmosphere` | 所有 | `["sdxl", "midjourney"]` | 大气效果通用 |
| `panel` | 所有 | `["sdxl", "midjourney"]` | 分镜通用 |
| `action-fx` | 所有 | `["sdxl", "midjourney"]` | 特效通用 |
| `character-fx` | 所有 | `["sdxl", "midjourney"]` | 角色特效通用 |
| `clothing` | 所有 | `["sdxl", "midjourney"]` | 服装通用 |
| `color-look` | 所有 | `["sdxl", "midjourney"]` | 色彩通用 |
| `era` | 所有 | `["sdxl", "midjourney"]` | 时代通用 |
| `held-prop` | 所有 | `["sdxl", "midjourney"]` | 道具通用 |
| `material` | 所有 | `["sdxl", "midjourney"]` | 材质通用 |
| `photographer` | 所有 | `["sdxl", "midjourney"]` | 摄影师风格通用 |
| `temporal` | 所有 | `["sdxl", "midjourney"]` | 时间效果通用 |
| `transitions` | 所有 | `["sdxl", "midjourney"]` | 转场通用 |

### 3.3 空值约定

- **compatibility 缺失或为空数组 = 通用**（适用于所有模型）
- 下游过滤示例：`GET /api/keywords?compatibility=sdxl` 返回 `compatibility` 包含 `sdxl` **或** `compatibility` 为空的关键词

### 3.4 迁移脚本伪代码

```python
# migrate_compatibility.py
import json, glob

CATEGORY_DEFAULTS = {
    "character": ["sdxl", "midjourney"],
    "scene": ["sdxl", "midjourney", "flux"],
    "shot-language": ["sdxl", "midjourney", "flux"],
    # ... 所有分类的默认值
}

SUBCATEGORY_OVERRIDES = {
    ("shot-language", "camera-move"): ["kling", "runway", "minimax_h3"],
    ("shot-language", "lens"): ["sdxl", "midjourney", "flux"],
    # ... 子分类覆盖

total = 0
updated = 0

for f in glob.glob("keywords/categories/*.json"):
    cat = f.split("/")[-1].replace(".json", "")
    with open(f, encoding="utf-8") as fp:
        data = json.load(fp)

    default = CATEGORY_DEFAULTS.get(cat, [])  # 空列表 = 通用（不设置）

    for kw in data:
        total += 1
        if not kw.get("compatibility"):  # 只处理没有 compatibility 的
            sub = kw.get("subcategory")
            override = SUBCATEGORY_OVERRIDES.get((cat, sub))
            kw["compatibility"] = override or default
            updated += 1

    with open(f, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

print(f"更新 {updated}/{total} 条关键词的 compatibility")
```

预期：约 6037 条全部获得默认 compatibility。

---

## Task 4 (API-2): 聚合统计端点

### 4.1 GET /api/stats 返回结构

```json
{
  "name": "Prompt Warehouse Stats",
  "version": "1.4.0",
  "generated_at": "2026-10-11T12:00:00Z",
  "total": 6037,
  "by_category": {
    "styles": 1990,
    "scene": 995,
    "clothing": 703,
    "shot-language": 38,
    "composition": 533,
    ...
  },
  "by_lifecycle": {
    "approved": 6037,
    "experimental": 0,
    "deprecated": 0
  },
  "by_score_bucket": {
    "< 0.5": 0,
    "0.5-0.7": 0,
    "0.7-0.9": 5723,
    ">= 0.9": 314
  },
  "by_compatibility": {
    "sdxl": 5800,
    "midjourney": 5900,
    "flux": 3200,
    "kling": 12,
    "runway": 12,
    "minimax_h3": 12
  },
  "missing_template_refs": [
    {
      "workflow_id": "workflow.comic_panel_full",
      "template_id": "character.reference_description",
      "step_order": 1
    },
    ...
  ],
  "data_quality": {
    "missing_term_zh": 0,
    "missing_labels_zh": 0,
    "duplicate_terms": 256,
    "orphan_template_refs": 17
  }
}
```

### 4.2 生成脚本（添加到 generate-api.py）

```python
def generate_stats():
    """全局统计 + 回归校验"""
    meta = json.load(open(REPO / "keywords" / "_meta.json", encoding="utf-8"))

    total = 0
    by_category = {}
    by_lifecycle = Counter()
    by_score_bucket = {"< 0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, ">= 0.9": 0}
    by_compatibility = Counter()
    missing_zh_term = 0
    missing_zh_labels = 0

    for f in glob.glob(str(REPO / "keywords" / "categories" / "*.json")):
        cat = Path(f).stem
        data = json.load(open(f, encoding="utf-8"))

        for kw in data:
            total += 1
            by_category[cat] = by_category.get(cat, 0) + 1

            lc = kw.get("lifecycle", "missing")
            by_lifecycle[lc] += 1

            s = kw.get("score", 0)
            if isinstance(s, (int, float)):
                if s < 0.5: by_score_bucket["< 0.5"] += 1
                elif s < 0.7: by_score_bucket["0.5-0.7"] += 1
                elif s < 0.9: by_score_bucket["0.7-0.9"] += 1
                else: by_score_bucket[">= 0.9"] += 1

            compat = kw.get("compatibility", [])
            if isinstance(compat, list):
                for c in compat:
                    by_compatibility[c] += 1
            else:
                # 空值 = 通用，计入所有模型
                for m in ["sdxl", "midjourney", "flux", "kling", "runway", "minimax_h3"]:
                    by_compatibility[m] += 1

            if not kw.get("term_zh"): missing_zh_term += 1
            if not kw.get("labels_zh"): missing_zh_labels += 1

    # 统计 orphan template refs
    orphan_refs = []
    existing_tids = set()
    for f in glob.glob(str(REPO / "templates" / "*.json")):
        data = json.load(open(f, encoding="utf-8"))
        if isinstance(data, list):
            for t in data:
                if t.get("id"): existing_tids.add(t["id"])
        elif isinstance(data, dict) and "id" in data:
            existing_tids.add(data["id"])

    for f in glob.glob(str(REPO / "workflows" / "*.json")):
        if "_meta" in f: continue
        wf = json.load(open(f, encoding="utf-8"))
        for step in wf.get("steps", []):
            tid = step.get("template_id")
            if tid and tid not in existing_tids:
                orphan_refs.append({
                    "workflow_id": wf["id"],
                    "template_id": tid,
                    "step_order": step.get("order")
                })

    stats = {
        "name": "Prompt Warehouse Stats",
        "version": meta.get("version"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "by_lifecycle": dict(by_lifecycle),
        "by_score_bucket": by_score_bucket,
        "by_compatibility": dict(by_compatibility),
        "missing_template_refs": orphan_refs,
        "data_quality": {
            "missing_term_zh": missing_zh_term,
            "missing_labels_zh": missing_zh_labels,
            "duplicate_terms": 256,  # 硬编码或动态计算
            "orphan_template_refs": len(orphan_refs)
        }
    }

    with open(API_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"✅ stats.json: {total} keywords, {len(by_category)} categories")
```

### 4.3 回归校验用法

每次部署后调用 `GET /api/stats`，与预期值对比：

```bash
# 校验脚本
curl -s "https://zz3656.github.io/prompt-warehouse/api/stats.json" | python3 << 'EOF'
import json, sys

stats = json.load(sys.stdin)

# 期望值（手动维护）
EXPECTED = {
    "total": 6037,
    "categories": 20,
    "missing_term_zh": 0,
    "orphan_template_refs": 17  # 修复后应为 0
}

errors = []
if stats["total"] != EXPECTED["total"]:
    errors.append(f"total 变化: {stats['total']} (期望 {EXPECTED['total']})")
if len(stats["by_category"]) != EXPECTED["categories"]:
    errors.append(f"分类数变化: {len(stats['by_category'])} (期望 {EXPECTED['categories']})")
if stats["data_quality"]["missing_term_zh"] != 0:
    errors.append(f"term_zh 缺失: {stats['data_quality']['missing_term_zh']}")
if stats["data_quality"]["orphan_template_refs"] != 0:
    errors.append(f"孤儿引用: {stats['data_quality']['orphan_template_refs']}")

if errors:
    print("❌ 回归校验失败:")
    for e in errors: print(f"  {e}")
    sys.exit(1)
else:
    print("✅ 回归校验通过")
EOF
```

---

## 执行清单（按依赖顺序）

| 序号 | 任务 | 优先级 | 依赖 | 产出 |
|------|------|--------|------|------|
| **1** | Task 1: angle/angles 合并 | D-2 | 无 | composition.json 更新、_meta.json 更新 |
| **2** | Task 2: 补全 12 个 template | P0 | 无（但 workflow 依赖） | 12 个 JSON 文件 + templates/_meta.json |
| **3** | Task 3: 新增 compatibility 字段 | P2 | 无 | 迁移脚本 + schema 更新 |
| **4** | Task 4: 聚合统计端点 | API-2 | 依赖 Task 1-3 的数据变更 | generate-api.py 更新 + stats.json 新结构 |

**建议执行顺序：** Task 1 → Task 2 → Task 3 → Task 4

- Task 1 和 Task 2 互不依赖，可并行
- Task 4 依赖前 3 项的数据产物（stats 需要最新的 total、compatibility 分布等）
- Task 2 完成后 workflow 引用全部解决，workflow 功能立即可用
