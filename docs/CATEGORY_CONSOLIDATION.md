# 分类精简方案 — Category Consolidation Plan

> 制定日期：2026-09-29
> 执行日期：2026-09-29
> 版本：v1.0.0 → v1.1.0
> 状态：✅ 已完成

**结果**：keywords/categories/ 从 **33 个文件精简到 20 个文件**，关键词总数 **5,959 → 5,957**（净减 2 个为 term 完全重复的 anamorphic lens + fisheye lens）。

---

## 1. 精简总览

| # | 操作 | 源文件 | 关键词数 | 目标位置 | 备注 |
|---|------|--------|---------|---------|------|
| 1 | 删除 | `style.json` | 49 | → `styles.json/art` | 与 styles.json/artStyles 子分类重叠 |
| 2 | 合并 | `aesthetic.json` | 42 | → `styles.json/aesthetic` | 保留主流/小众，剔除与 wardrobe/era 重复 |
| 3 | 合并 | `atmosphere.json` | 40 | → `lighting.json/atmosphere` | 天气/大气效果归入灯光类 |
| 4 | 合并 | `mood.json` | 51 | → `character.json/mood` | 表情与 character/expression 合并 |
| 5 | 合并 | `pose.json` | 81 | → `character.json/pose` | 替换原 character.json/pose 的 43 个 |
| 6 | 合并 | `wardrobe.json` | 70 | → `clothing.json/wardrobe-*` | 服装搭配归入 clothing |
| 7 | 合并 | `setting.json` | 51 | → `scene.json/indoor\|urban\|fantastical\|nature` | 场景设定合并 |
| 8 | 合并 | `backdrop.json` | 40 | → `scene.json/backdrop` | 摄影棚背景合并 |
| 9 | 合并 | `lens.json` | 18 | → `composition.json/lens` | 镜头类型合并 |
| 10 | 合并 | `camera-format.json` | 31 | → `composition.json/camera-format` | 相机型号合并 |
| 11 | 合并 | `camera-motions.json` | 66 | → `composition.json/camera-motions` | 摄影机运动合并 |
| 12 | 合并 | `photo-genre.json` | 24 | → `photographer.json/genre` | 摄影流派合并 |
| 13 | 合并 | `post-process.json` | 18 | → `color-look.json/post-process` | 后期处理合并 |

**合计**：13 次合并操作，删除 13 个文件，新增 0 个文件，关键词数不变 (5,959)。

---

## 2. 子分类映射明细

### 2.1 styles.json（吸收 style.json + aesthetic.json）

**保留现有子分类**：
- mj_v5_design (419), mj_v5_digital (366), mj_v5_mediums (318), mj_v5_themes (307)
- mj_v5_colors (180), mj_v5_colors2 (68), mj_v5_dimension (28), mj_v5_intangibles (2), mj_v5_artists (2)
- artStyles (42), artistStyle (30), animeManga (30), specialty (23), realism (14)

**新增子分类**：
- `art` ← style.json/art (49)
- `aesthetic` ← aesthetic.json/mainstream (16) + niche (17) — **剔除**:
  - aesthetic/era (4) → era.json（重复）
  - aesthetic/mood (5) → character.json/mood（重复）

### 2.2 lighting.json（吸收 atmosphere.json）

**保留现有子分类**：
- mj_v5_lighting (162), mj_v5_sfx (99), dynamic (21), mood (20), natural (17), special (12), dramatic (12)

**新增子分类**：
- `atmosphere` ← atmosphere.json 全部 (40)

### 2.3 character.json（吸收 mood.json + pose.json）

**保留现有子分类**：
- hair, hairColors, eyes, eyeColors, expression, anatomy, bodyType, body, skin, age, accessories, effects, detail, composition, face, character, clothing

**新增子分类**：
- `mood` ← mood.json 全部 (51)
- `pose` ← pose.json 全部 (81) **替代** 现有 character.json/pose (43)

### 2.4 clothing.json（吸收 wardrobe.json）

**保留现有子分类**：
- mj_v5_materials (377), mj_v5_matprops (134), accessories (50), outfits (34), tops (13), bottoms (9)

**新增子分类**：
- `wardrobe-archetype` ← wardrobe.json/archetype (10)
- `wardrobe-top` ← wardrobe.json/top (7)
- `wardrobe-bottom` ← wardrobe.json/bottom (6)
- `wardrobe-outerwear` ← wardrobe.json/outerwear (7)
- `wardrobe-footwear` ← wardrobe.json/footwear (6)
- `wardrobe-headwear` ← wardrobe.json/headwear (6)
- `wardrobe-accessories` ← wardrobe.json/accessories (7)
- `wardrobe-color-palette` ← wardrobe.json/color-palette (7)
- `wardrobe-material` ← wardrobe.json/material (7)
- `wardrobe-era` ← wardrobe.json/era (7) — **注**：与 era.json 内容不同（wardrobe/era 描述时尚年代，era.json 描述历史时代）

### 2.5 scene.json（吸收 setting.json + backdrop.json）

**保留现有子分类**：
- mj_v5_nature (324), mj_v5_objects (248), mj_v5_geo (167), nature (61), interaction (57), mj_v5_space (53), weather (35), relationship (22), time (20)

**新增子分类**：
- `indoor` ← setting.json/indoor (23)
- `urban` ← setting.json/urban (10)
- `fantastical` ← setting.json/fantastical (7)
- `backdrop` ← backdrop.json 全部 (40)
  - 内含 solid/gradient/textured/fabric/effect/reflective

### 2.6 composition.json（吸收 lens.json + camera-format.json + camera-motions.json）

**保留现有子分类**：
- mj_v5_camera (190), mj_v5_structure (67), mj_v5_perspective (55), angles (14), framing (10), rules (9), mj_v5_geometry (4)

**新增/合并**：
- `lens` ← 原 composition.json/lens (14) + lens.json 全部 (18) — **剔除**: lens.json/anamorphic (与 camera-format.json/anamorphic 重复)
- `camera-format` ← camera-format.json 全部 (31)
- `camera-motions` ← camera-motions.json 全部 (66)
- **保留原 `composition.json/lens`** 不变 (但合并 lens.json 后应叫 `lens-focal` 或类似以避免混淆？)

> **决策**：保留 `lens` 子分类名，合并后该子分类共 14+17=31 个镜头相关词。

### 2.7 photographer.json（吸收 photo-genre.json）

**保留现有子分类**：
- editorial (31), illustrator (13), concept (8), documentary (7), cinematographer (4)

**新增子分类**：
- `genre` ← photo-genre.json 全部 (24)
  - 含 editorial (10, 部分重复)、documentary (2, 重复)、studio-formal (6)、selfie (4)、commercial (1)、print-context (1)

### 2.8 color-look.json（吸收 post-process.json）

**保留现有子分类**：
- film-emulation (20), palette (13), social-preset (8)

**新增子分类**：
- `post-process` ← post-process.json 全部 (18)
  - 含 vignette/dodge/film/halation/bloom/chromatic/light/scratched/color/soft/contrast/sharpening/clarity/dehaze/lift

---

## 3. 字段处理规则

### 3.1 id 重写

每个合并的关键词都需要重写 `id` 字段以符合 `{category}_{subcategory}_{slug}` 规范：

| 场景 | 规则 |
|------|------|
| 子分类名变化 | id 前缀 `{old_category}_{old_subcategory}_` → `{new_category}_{new_subcategory}_` |
| 子分类名不变（如 character.json/pose → character.json/pose）| 保留原 id，必要时加随机后缀避免冲突 |
| id 冲突（极少概率） | 加 `_m` 后缀或顺序编号 |

### 3.2 category 字段更新

`category` 字段必须更新到新的分类名。

### 3.3 subcategory 字段更新

按上方映射表更新。

### 3.4 其他字段

保留原值（term, term_zh, aliases, labels, score, priority, lifecycle, tags, created_at, updated_at, source, usage_count, success_rate, notes, variations）。

---

## 4. 冲突检测规则

合并前必须运行 `tools/pws-dedup.py --scan-all` 确保：

1. **id 唯一性**：合并后的所有 id 全局唯一
2. **term 唯一性**：跨分类同 term 需评估（部分允许，如 era/wardrobe/era 可能并存）
3. **跨分类同 term 警告**：仅作 warning，不阻断合并

---

## 5. 验证步骤

合并脚本完成后：

1. **id 唯一性检查**：`jq -r '.id' *.json | sort | uniq -d` 应为空
2. **关键词总数对比**：合并前 `5959` = 合并后 `5959`
3. **分类数量对比**：合并前 `33` → 合并后 `19`（删 13，加 0）
4. **JSON Schema 校验**：每个文件能通过 schema/keyword.schema.json
5. **运行 `pws-dedup.py --dedup-only`** 各文件无内部重复

---

## 6. 文档更新

合并后需更新：

| 文件 | 更新内容 |
|------|---------|
| `STANDARD.md` §3.2 | 更新分类体系（33 → 19），附录 A 同步 |
| `STANDARD_en.md` §3.2 | 同上 |
| `README.md` | 更新分类列表 |
| `README_en.md` | 同上 |
| `keywords/_meta.json` | `total_categories`: 33 → 19，加 `consolidation` 版本号 |

---

## 7. 不在本次精简范围

- `character-fx.json` (55) 与 `action-fx.json` (72) 边界可优化，但需要更深入的人工判断语义重叠，本次暂不动
- `transitions.json` (81) 仅视频场景用，保留独立
- `temporal.json` (18) 太小但语义独立（时间效果），保留
- `material.json` (67) 独立维度，保留
- `render-quality.json` (24) 与 quality 略重复，但子分类独特，保留
- `negative.json` (103) 重要，保留
- `panel.json` (69) 漫画专用，必保留
- `held-prop.json` (60) 与 character/accessories 部分重叠，但"手持"语义独立，保留
- `framing.json` (66) — 子分类 shot-size/composition/coverage/angle/vantage 与 composition.json/lens 等略重叠，本次**保留**作为摄影构图专用
