# Prompt Warehouse 项目介绍

## 概述

Prompt Warehouse (PWS) 是一个结构化的 AI 图像/视频生成提示词管理系统，为 PanelCraft 提供关键词数据、模板引擎和配方包（Bundles）API。

**当前版本：v1.2.0**
- 6,037 个结构化关键词
- 20 个分类 · 156 个子分类
- 12 个配方包 (Bundles)
- 15 个模板 (Templates)

## 数据规模

### 关键词分布（按分类，降序）
- styles: 1990 条
- scene: 995 条
- clothing: 703 条
- composition: 533 条
- character: 477 条
- lighting: 382 条
- quality: 166 条
- negative: 103 条
- photographer: 89 条
- transitions: 81 条
- action-fx: 75 条
- panel: 74 条
- color-look: 69 条
- material: 67 条
- held-prop: 66 条
- character-fx: 60 条
- shot-language: 38 条
- era: 33 条
- temporal: 30 条
- atmosphere: 6 条

### 子分类分布（按分类）
- action-fx: 7 个子分类
- atmosphere: 1 个子分类
- character: 18 个子分类
- character-fx: 5 个子分类
- clothing: 16 个子分类
- color-look: 4 个子分类
- composition: 14 个子分类
- era: 3 个子分类
- held-prop: 9 个子分类
- lighting: 8 个子分类
- material: 7 个子分类
- negative: 7 个子分类
- panel: 4 个子分类
- photographer: 6 个子分类
- quality: 14 个子分类
- scene: 13 个子分类
- shot-language: 3 个子分类
- styles: 16 个子分类
- temporal: 4 个子分类
- transitions: 8 个子分类

## 字段覆盖率（100%）

- term_zh: 100% ✅
- compatibility: 100%（全显式绑定，无空值）✅
- weight: 100% ✅（PanelCraft 排序用，0-1）
- source: 100% ✅
- is_negative: 103 条（负面词，weight=0.5，独立通道）
- relation_group: 314 条（139 组跨分类重复，canonical/variant）
- subcategory_group: 3484 条（midjourney_v5 分组）

## Compatibility 模型绑定

| 模型 | 数量 |
|------|------|
| sdxl | 6,025 |
| midjourney | 6,025 |
| flux | 1,849 |
| kling | 12（视频专用）|
| runway | 12（视频专用）|
| minimax_h3 | 12（视频专用）|

## Bundle 配方包

- **character.animesque_portrait**: 24 关键词, templates=无
- **character.cosplay_portrait**: 20 关键词, templates=无
- **environment.architectural_interior**: 23 关键词, templates=无
- **environment.cityscape_exterior**: 22 关键词, templates=无
- **fashion.editorial_shoot**: 21 关键词, templates=无
- **food.editorial_style**: 21 关键词, templates=无
- **photography.cinematic_portrait**: 39 关键词, templates=video.prompts, video.prompts
- **portrait.cinematic**: 20 关键词, templates=无
- **product.ecommerce_packshot**: 17 关键词, templates=无
- **product.packaging_mockup**: 19 关键词, templates=无
- **scene.cyberpunk**: 20 关键词, templates=无
- **scene.fantasy_landscape**: 26 关键词, templates=无

## Templates（15 个唯一 ID）
- action.motion
- atmosphere.weather
- camera.movement
- camera.shot_type
- character.multiple_views
- character.reference_description
- color.grading
- lighting.mood
- llm.system_prompts
- panel.composition
- quality.character
- quality.standard
- scene.environment
- text.negative_keywords
- video.prompts

## 数据模型

### 关键词 (keywords/categories/*.json)
每个分类一个 JSON 数组，包含：
- id: {category}.{subcategory}_{slug}
- term: 英文关键词
- term_zh: 中文翻译
- category / subcategory: 分类与子分类
- weight: 0-1 组合权重（PanelCraft 排序用）
- score: 质量评分（同 weight 时次级排序）
- is_negative: true 表示负面词（独立通道，不参与正面排序）
- compatibility: 兼容模型列表 [sdxl, midjourney, flux, kling, runway, minimax_h3]
- source: 数据来源（MidJourney Reference / @nodaro/prompts / h3-comic-builder 等）
- relation_group: 跨分类去重组
- subcategory_group: 逻辑分组（如 midjourney_v5）

### Bundle (bundles/*.json)
配方包 = 关键词列表 + 模板引用，bundle_type: keywords_only / with_template

### Template (templates/*.json)
提示词模板，支持变量替换和 variant 切换

## API 接口

### PanelCraft Bundles API (docs/bundles-api.json)
- GET /api/bundles — 列出所有 bundle
- GET /api/bundles/:id — 读取单个 bundle
- PUT /api/bundles/:id — 更新 bundle（PanelCraft 调用）
- POST /api/bundles — 新建 bundle
- DELETE /api/bundles/:id — 删除 bundle

## 工具链

- scripts/validate-json.sh — JSON 语法校验
- tools/pws-index.py — 索引生成（keywords/templates/workflows）
- docs/panelcraft-sorting.md — PanelCraft 排序建议
- docs/panelcraft-categories.json — 分类白名单（core/extended/optional）

## 技术栈

- 纯 JSON 数据，无数据库依赖
- Python CLI 工具链（索引、审计、校验）
- REST API 供 PanelCraft 读写 bundles
- Git 版本控制，pre-commit 校验

## 待优化方向（供 AI 评估）

1. **排序算法**：weight + score 双键排序，负面词分离，compatibility 过滤
2. **Bundle 模板引用**：12 个 bundle 中仅 1 个引用模板（photography.cinematic_portrait 用 video.prompts），其余 11 个为纯关键词配方
3. **Source 追溯**：已 100% 覆盖，但早期批次来源标记可更精细
4. **compatibility 过滤**：图像/视频模型精确匹配，无空值约定
5. **子分类命名**：已统一小写，mj_v5_ 前缀通过 subcategory_group 分组
6. **PanelCraft UI**：按 bundle_type 区分显示方式（纯关键词 vs 含模板）
