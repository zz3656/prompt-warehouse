# 提示词仓库标准（PWS）

**一个统一的、与语言无关的标准，用于跨项目组织、版本控制和共享 AI 生成提示词。**

> **pws v1.0** | **简体中文** | [English](README_en.md)
> **当前数据版本**: v1.8.0 (6,015 关键词 · 20 分类 · **100% term_zh 覆盖**)
>
> **仓库地址**: https://github.com/zz3656/prompt-warehouse
> **许可证**: MIT

---

## 📖 目录

- [概述](#-概述)
- [功能](#-功能)
- [目录结构](#-目录结构)
- [快速开始](#-快速开始)
- [数据模型](#-数据模型)
- [模板语法](#-模板语法)
- [配方包（Bundles）](#-配方包bundles)
- [版本控制](#-版本控制)
- [API 集成](#-api-集成)
- [多语言支持](#-多语言支持)
- [项目状态](#-项目状态)
- [贡献](#-贡献)
- [许可证](#-许可证)

---

## 🌟 概述

提示词仓库标准（PWS）是一个基于 JSON 的规范，用于管理 AI 生成提示词。它解决了常见问题：

- **告别数据孤岛**：在所有 AI 项目（图像、视频、文本、音乐）之间共享关键词和模板
- **版本控制**：追踪哪个版本的提示词产生了什么结果
- **结构化数据**：带有完整元数据（评分、生命周期、使用分析）的机器可读 JSON
- **跨项目发现**：基于标签的分类系统让你即时找到正确的关键词
- **生命周期管理**：草稿 → 审核 → 批准 → 归档 的流程管道

---

## ✨ 功能

| 功能 | 说明 |
|------|------|
| **结构化关键词** | 每个关键词都是一个富对象，带有元数据——评分、优先级、生命周期、使用统计 |
| **分类体系** | 9 个顶级分类及其嵌套子分类（质量、角色、服装、风格等） |
| **模板引擎** | 类 Mustache 语法，支持条件（`{{#if}}`）、迭代（`{{#each}}`）和辅助函数 |
| **项目配置** | 每个项目的 JSON 配置文件，可启用/禁用分类和模板 |
| **快照系统** | 导出带有完整上下文的快照，用于追踪生成结果 |
| **迁移支持** | 内置从遗留 `.js` 文件迁移的路径 |
| **多语言** | 关键词和模板支持 EN / ZH / JA 标签 |

---

## 📁 目录结构

```
prompt-warehouse/
├── schema/                     # JSON Schema 定义（机器可读）
│   ├── keyword.schema.json     # 关键词数据结构
│   ├── template.schema.json    # 模板数据结构
│   └── project.schema.json     # 项目配置结构
├── keywords/                   # 关键词词典（"数据库"）
│   ├── _meta.json              # 全局元数据 + 版本信息
│   └── categories/             # 每个顶级分类一个文件
│       ├── quality.json        # 质量提升词
│       ├── composition.json    # 构图 / 构图与镜头
│       ├── lighting.json       # 灯光与氛围
│       ├── character.json      # 角色外观属性
│       ├── clothing.json       # 服装与配饰
│       ├── styles.json         # 艺术风格
│       ├── negative.json       # 负面提示词
│       ├── scene.json          # 场景与环境
│       └── panel.json          # 漫画分镜特效
├── templates/                  # 提示词模板
│   ├── _meta.json              # 模板元数据
│   └── _all_templates.json     # 全部模板（原始数据）
├── projects/                   # 项目配置
│   └── h3-comic-builder.json   # H3 漫画构建器配置
├── snapshots/                  # 导出快照
│   └── YYYY/MM/
└── STANDARD.md                 # 完整标准文档
```

---

## 🚀 快速开始

### 1. 浏览关键词

每个分类文件都是一个普通的 JSON 数组。打开任意文件即可浏览：

```bash
# 查看所有质量关键词
cat keywords/categories/quality.json | head -50

# 搜索特定术语
grep -r '"term": "blonde hair"' keywords/categories/character.json
```

### 2. 使用模板

模板支持变量替换。`_all_templates.json` 文件包含所有 27 个模板的完整元数据：

```json
// 角色参考描述模板
{
  "id": "character.reference_description",
  "name": "Character Reference Description",
  "name_zh": "角色参考描述",
  "variables": ["gender", "age", "hair_color", "hair_style", "eye_color", "skin_tone"],
  "example_output": "girl 16 years old white long hair blue eyes fair skin"
}
```

### 3. 配置项目

编辑项目配置文件以启用/禁用分类和模板：

```bash
cat projects/h3-comic-builder.json
```

---

## 🗂️ 数据模型

### 关键词模型

每个关键词都是一个带有丰富元数据的结构化 JSON 对象：

```json
{
  "id": "qc_graceful_lighting",
  "term": "graceful lighting",
  "term_zh": "优雅的灯光",
  "category": "quality",
  "subcategory": "lighting",
  "labels": ["lighting", "glow", "illumination"],
  "labels_zh": ["灯光", "光影", "光线"],
  "score": 0.92,
  "priority": "high",
  "lifecycle": "approved"
}
```

### 关键字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识符，格式：`{category}_{subcategory}_{slug}`，如 `quality_basic_masterpiece` |
| `term` | string | ✅ | 标准提示词（英文），如 `masterpiece` — 用于 API 检索和模板变量 |
| `term_zh` | string | ✅ | 中文翻译，如 `杰作` — 其他项目按此字段做中文检索 |
| `aliases` | string[] | | 英文替代术语，如 `["best work", "top tier"]` |
| `aliases_zh` | string[] | | 中文替代说法，如 `["最佳作品", "顶级"]` |
| `category` | string | ✅ | 顶级分类，共 20 类（见下方分类体系） |
| `subcategory` | string | ✅ | 子分类，如 `basic`, `hair`, `anime` |
| `labels` | string[] | | 英文扁平搜索标签，如 `["quality", "booster"]` |
| `labels_zh` | string[] | | 中文扁平搜索标签，如 `["质量", "增强"]` — 中文过滤专用 |
| `score` | number | | 质量评分 0–1（默认：0.5），0.90+ 为行业验证，0.70–0.89 为可靠常用 |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` → `review` → `approved` → `deprecated` → `archived` |
| `tags` | string[] | | 用户自定义标签，跨切面标记 |
| `source` | string | | 数据来源，如 `willwulfken/MidJourney-Styles-and-Keywords-Reference` |
| `usage_count` | number | | 使用次数（默认：0），由调用方项目更新 |
| `success_rate` | number | | 生成成功率 0–1（默认：null），由调用方项目更新 |
| `created_at` | string | | ISO 8601 创建时间戳 |
| `updated_at` | string | | ISO 8601 更新时间戳 |
| `notes` | string | | 备注信息 |
| `variations` | array | | 上下文相关变体，`[{"term": "platinum blonde", "context": "高价值角色"}]` |

### 模板字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 模板唯一标识符，如 `h3.video_prompts` |
| `name` / `name_zh` | string | ✅ | 模板中英文名称 |
| `description` / `description_zh` | string | | 模板中英文描述 |
| `category` | string | | 所属分类 |
| `subcategories` | string[] | | 子分类列表 |
| `api_targets` | string[] | | 适配的 AI 模型，如 `["SDXL", "Minimax H3"]` |
| `lifecycle` | enum | | `draft` / `review` / `approved` / `deprecated` / `archived` |
| `score` | number | | 质量评分 0–1 |
| `variables` | array | | 模板变量定义，`[{"name": "subject", "type": "string", "required": true}]` |
| `variants` | array | ✅ | 变体列表，每个含 `id`, `description`, `description_zh`, `template` |
| `examples` | array | | 使用示例 |

### 项目配置字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` / `name` | string | 项目唯一标识符和名称 |
| `project_type` | enum | `comic` / `video` / `game` / `web` / `text` / `music` / `general` |
| `keywords.enabled_categories` | string[] | 启用的关键词分类 |
| `templates.enabled` | string[] | 启用的模板 ID 列表 |
| `settings.default_api` | string | 默认 AI 模型 |
| `settings.max_prompt_length` | integer | 最大提示词长度 |

### 其他项目调用示例

其他项目可以直接读取 `keywords/categories/` 下的 JSON 文件，每个关键词都包含 **中英双语字段**，方便跨语言检索：

```json
{
  "id": "quality_basic_masterpiece",
  "term": "masterpiece",          // 英文检索
  "term_zh": "杰作",               // 中文检索 ← 中文项目用这个字段
  "category": "quality",
  "subcategory": "basic",
  "labels": ["quality", "booster"],
  "labels_zh": ["质量", "增强"],   // 中文过滤 ← 中文项目用这个字段
  "score": 0.95,
  "priority": "high",
  "lifecycle": "approved"
}
```

**快速浏览所有分类**：`ls keywords/categories/` 列出 20 个分类文件。
**完整数据模型**：[STANDARD.md](STANDARD.md)
**JSON Schema**：[schema/keyword.schema.json](schema/keyword.schema.json) · [schema/template.schema.json](schema/template.schema.json)

### 分类体系

| 分类 | Slug | 说明 |
|------|------|------|
| 质量 | `quality` | AI 输出质量提升词 |
| 构图 | `composition` | 构图、角度、镜头效果 |
| 灯光 | `lighting` | 灯光类型与氛围 |
| 角色 | `character` | 角色外观属性 |
| 服装 | `clothing` | 服装与配饰 |
| 风格 | `styles` | 艺术与渲染风格 |
| 负面 | `negative` | 负面提示词 |
| 场景 | `scene` | 场景与环境 |
| 分镜 | `panel` | 分镜特效 |
| 动作特效 | `action-fx` | 动作与特效（灾害、火焰、战斗、魔法）— @nodaro/prompts |
| 美学微趋势 | `aesthetic` | Y2K, dark academia, cottagecore 等 — @nodaro/prompts |
| 大气效果 | `atmosphere` | 雾、雨、粒子、神光 — @nodaro/prompts |
| 背景预设 | `backdrop` | 纯色、渐变、纹理背景 — @nodaro/prompts |
| 画幅格式 | `camera-format` | IMAX、电影宽屏等 — @nodaro/prompts |
| 镜头运动 | `camera-motions` | 推拉摇移跟 — @nodaro/prompts |
| 角色特效 | `character-fx` | 狼人、吸血鬼、赛博格等 — @nodaro/prompts |
| 色彩分级 | `color-look` | 暖色、冷色、胶片模拟 — @nodaro/prompts |
| 历史时代 | `era` | 中世纪、维多利亚、赛博朋克等 — @nodaro/prompts |
| 构图与景别 | `framing` | 特写、中景、全景 — @nodaro/prompts |
| 手持道具 | `held-prop` | 武器与道具 — @nodaro/prompts |
| 镜头与焦距 | `lens` | 14mm-400mm — @nodaro/prompts |
| 材质预设 | `material` | 织物、金属、石材、木材 — @nodaro/prompts |
| 角色情绪 | `mood` | 喜怒哀乐等情绪 — @nodaro/prompts |
| 摄影类型 | `photo-genre` | 时尚、纪实、证件照等 — @nodaro/prompts |
| 摄影师风格 | `photographer` | Ansel Adams, Annie Leibovitz 等 — @nodaro/prompts |
| 姿态手势 | `pose` | 站姿、坐姿、行走等 — @nodaro/prompts |
| 后期特效 | `post-process` | 暗角、胶片颗粒、色散等 — @nodaro/prompts |
| 渲染引擎 | `render-quality` | Unreal 5, Octane, Cycles 等 — @nodaro/prompts |
| 场景环境 | `setting` | 室内、城市、自然、奇幻 — @nodaro/prompts |
| 艺术风格 | `style` | 3D 渲染、动漫、水彩等 — @nodaro/prompts |
| 时间效果 | `temporal` | 慢动作、快速、时间冻结 — @nodaro/prompts |
| 转场效果 | `transitions` | 溶解、缩放、滑动 — @nodaro/prompts |
| 服装搭配 | `wardrobe` | 服装搭配方案 — @nodaro/prompts |

### 子分类亮点

**质量** — `basic` · `advanced` · `anime`
> masterpiece, best quality, ultra-detailed, 8k resolution · 杰作 · 最高质量 · 超细节

**角色** — `hair` · `hairColors` · `eyes` · `eyeColors` · `expression` · `pose` · `anatomy` · `bodyType` · `skin` · `age`
> white long hair, blue eyes, fair skin, determined expression · 白色长发 · 蓝眼睛 · 白皙皮肤 · 坚定的表情

**服装** — `tops` · `bottoms` · `outfits` · `accessories` · `mj_v5_materials` · `mj_v5_matprops`
> school uniform, white blouse, pleated skirt, red ribbon · 校服 · 白衬衫 · 百褶裙 · 红丝带

**风格** — `anime` · `art` · `realism` · `specialty` · `artist` · `mj_v5_colors` · `mj_v5_colors2` · `mj_v5_design` · `mj_v5_digital` · `mj_v5_dimension` · `mj_v5_intangibles` · `mj_v5_mediums` · `mj_v5_themes` · `mj_v5_artists`
> anime style, cel shading, manga comic style · 动漫风格 · 赛璐珞上色 · 漫画风格

**负面** — `quality` · `anatomy` · `face` · `composition` · `style` · `text` · `commonDefects`
> low quality, worst quality, bad anatomy, extra limbs · 低质量 · 最差质量 · 畸形解剖 · 多余肢体

**灯光** — `natural` · `dramatic` · `mood` · `dynamic` · `special` · `mj_v5_lighting` · `mj_v5_sfx`
> golden hour, cinematic lighting, volumetric rays · 黄金时段 · 电影灯光 · 体积光

**构图** — `framing` · `angles` · `lens` · `rules` · `mj_v5_camera` · `mj_v5_geometry` · `mj_v5_perspective` · `mj_v5_structure`
> close-up, wide shot, eye level, Dutch angle · 特写 · 广角 · 平视 · 荷兰角

**场景** — `relationship` · `interaction` · `weather` · `time` · `mj_v5_geo` · `mj_v5_nature` · `mj_v5_objects` · `mj_v5_space`
> school rooftop, cozy bedroom, battlefield, urban street · 学校屋顶 · 温馨卧室 · 战场 · 城市街道

**分镜** — `panelLayout` · `comicEffects` · `animation` · `panelMood`
> speed lines, motion blur, impact frames, screen tone · 速度线 · 动态模糊 · 冲击帧 · 网点纸

### 生命周期状态

```
草稿 → 审核 → 批准 → 归档
draft → review → approved → archived
              ↕           ↕
          (被拒绝)   (被弃用)
deprecated ↗
```

- **草稿 (draft)**：新添加，尚未验证
- **审核 (review)**：已提交审核，等待批准
- **批准 (approved)**：已验证，可用于生产
- **归档 (archived)**：不再使用，保留供参考

---

## 💡 提示词示例

### 漫画分镜提示词

**完整分镜正面提示词：**

```
masterpiece, best quality, ultra-detailed, girl 16 years old white long hair blue eyes fair skin, medium shot, character centered in frame, School Rooftop, golden hour, warm sunset glow, backlit rim light, long shadows, dialogue: "Hello!"
```

**完整分镜负面提示词：**

```
low quality, worst quality, bad anatomy, extra limbs, poorly drawn face, mutation, cropped, watermark, text, signature
```

**角色一致性参考：**

```
girl 16 years old white long hair blue eyes fair skin, full body character reference sheet on white background, multiple views: front view, side profile view, back view, three-quarter view, multiple facial expressions: happy, sad, angry, surprised, neutral
```

### 场景描述词

**户外场景：**

```
school rooftop at sunset, golden hour lighting, long shadows stretching across the ground, wind blowing through white hair, cherry blossom petals floating in the air, city skyline visible in the distance
```

**室内场景：**

```
cozy bedroom, warm lamp light, books on shelves, window with curtains, afternoon sunlight streaming through, personal photos on the wall, tidy room
```

**战斗场景：**

```
dramatic low angle shot, dynamic action pose, punch forward, motion blur, debris flying, intense determined expression, high contrast lighting, dramatic shadows, cinematic composition
```

### 模板示例

使用**角色参考模板**：

```json
{
  "gender": "girl",
  "age": "16",
  "hair": { "color": "white", "length": "long", "style": "twin tails" },
  "eyes": { "color": "blue", "shape": "almond" },
  "skin": "fair",
  "distinctive_features": ["red ribbon", "school uniform"]
}
```

**渲染输出：**

```
girl 16 years old white long twin tails hair blue almond eyes fair skin, red ribbon, school uniform
```

---

## 📝 模板语法

模板使用类 Mustache 语法，支持变量占位符：

| 语法 | 说明 | 示例 |
|------|------|------|
| `{{var}}` | 简单替换 | `{{hair_color}}` → `blonde` |
| `{{#if var}}...{{/if}}` | 条件渲染 | `{{#if age}} {{age}} 岁{{/if}}` |
| `{{#each arr}}...{{/each}}` | 数组迭代 | `{{#each features}}, {{this}}{{/each}}` |
| `{{join arr ', '}}` | 连接辅助 | `{{join styles ' | '}}` |
| `{{truncate text 50}}` | 截断到 50 字符 | `{{truncate desc 50}}` |

---

## 📦 版本控制

仓库遵循语义化版本控制：

| 类型 | 含义 |
|------|------|
| **主版本 (1.x.x)** | 结构变更，破坏性格式变更 |
| **次版本 (x.1.x)** | 新分类或字段，向后兼容 |
| **修订版 (x.x.1)** | 修复、数据修正、新增关键词 |

每个 `_meta.json` 都跟踪版本、结构版本和变更日志。

当前版本：**v1.8.0** — 20 个分类共 6,015 个关键词（**全部** 6,015 个有中文翻译，**100%** 覆盖）。

### 新增功能

| 功能 | 说明 |
|------|------|
| **配方包系统** | `bundles/` 目录 + `pws-bundles.py` 工具 — 预组合关键词配方 |
| **Bundle 工具** | `list` / `show` / `resolve` / `info` / `validate` 五个命令 |

---

## 📦 配方包（Bundles）

配方包是预组合的关键词 ID 列表，带有权重和模板引用，形成可复用的提示词配方。一个配方包可以引用数十个关键词，生成即开即用的提示词。

### 使用方法

```bash
# 列出所有配方包
python3 tools/pws-bundles.py list

# 查看配方包的预建提示词
python3 tools/pws-bundles.py show photography.cinematic_portrait

# 生成自定义提示词（替换变量）
python3 tools/pws-bundles.py resolve photography.cinematic_portrait \
    --subject "a young woman" --setting "coastal cliff at sunset"

# 查看详细关键词权重
python3 tools/pws-bundles.py info photography.cinematic_portrait

# 验证所有配方包
python3 tools/pws-bundles.py validate
```

### 当前配方包

| 配方包 | 关键词数 | 说明 |
|--------|----------|------|
| `photography.cinematic_portrait` | 39 | 电影感人像配方：质量保障 + 85mm 人像镜头 + 电影灯光 |
| `scene.fantasy_landscape` | 26 | 奇幻风景配方：风景 + 体积光 + 空灵氛围 |

### 格式说明

- **关键词权重 (0–1)**: 控制每个关键词在最终提示词中的优先级
- **强制包含 (`force_include`)**: 确保某些关键词（如质量保障、负面词）始终出现
- **预建提示词**: 可直接使用的完整 prompt
- **模板引用**: 可关联 API 特定的模板（如 `h3.video_prompts`）

详细文档见 [ADDING_BUNDLES.md](ADDING_BUNDLES.md)。

---

## 🔌 API 集成

PWS 设计用于与 REST API 配合使用。h3-comic-builder 服务器已提供：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/keywords` | GET | 列出关键词（分页、可筛选） |
| `/api/keywords/search` | GET | 全文搜索 |
| `/api/templates` | GET | 列出模板 |
| `/api/templates/:id/render` | POST | 用数据渲染模板 |
| `/api/snapshots` | GET/POST | 列出或创建快照 |

---

## 🌍 多语言支持

关键词和模板支持多语言：

```json
{
  "term": "graceful lighting",
  "term_zh": "优雅的灯光",
  "labels": ["lighting", "glow"],
  "labels_zh": ["灯光", "光影"]
}
```

---

## 📊 项目状态

| 阶段 | 状态 | 详情 |
|------|------|------|
| **阶段一：结构定义** | ✅ 完成 | 定义了 3 个 JSON 结构并验证 |
| **阶段二：数据迁移** | ✅ 完成 | 从 h3-comic-builder + MJ 参考迁移了 6,015 个关键词 |
| **阶段三：工具开发** | ✅ 完成 | 13 个 CLI 工具（索引、审计、翻译、去重、Bundle 管理等） |
| **阶段四：共享发布** | 📋 计划中 | 远程同步、团队协作、模板市场 |

---

## 🤝 贡献

我们欢迎贡献！以下是参与方式：

1. **Fork** 本仓库
2. **浏览** `keywords/categories/` 中的现有关键词
3. **添加** 新关键词，遵循 `schema/keyword.schema.json` 中的结构
4. **提交** Pull Request

指南：
- `term` 使用英文（标准形式）
- 添加 `labels` 以便搜索
- 设置适当的 `score` 和 `priority`
- 遵循 `{category}_{subcategory}_{slug}` 的 id 命名规范
- 在设置 `lifecycle: "approved"` 之前，先用生成测试验证现有关键词

---

## 📄 许可证

MIT 许可证 — 详见 [STANDARD.md](STANDARD.md)。

---

## 📚 资源

- **完整规范**: [STANDARD.md](STANDARD.md)
- **关键词结构**: [schema/keyword.schema.json](schema/keyword.schema.json)
- **模板结构**: [schema/template.schema.json](schema/template.schema.json)
- **Bundle 结构**: [schema/bundle.schema.json](schema/bundle.schema.json)
- **管理工具**: [tools/pws-bundles.py](tools/pws-bundles.py)
- **创建配方包**: [ADDING_BUNDLES.md](ADDING_BUNDLES.md)
- **元数据**: [keywords/_meta.json](keywords/_meta.json)
- **数据来源**: 见下文
- **当前统计**: 6,015 个关键词 · 20 个分类 · 4 个模板 · 2 个配方包

## 📥 数据来源（永久记录）

> **如何快速了解提示词来源**：查看 `keywords/_meta.json` 的 `data_sources` 字段和每个关键词的 `source` 字段，无需重新搜索。

| 来源 | 类型 | 关键词数 | 涵盖分类 |
|------|------|----------|----------|
| h3-comic-builder 中间件（JS 原始文件已迁移） | *已迁移* | 859 | 全部 9 类 — 这些关键词本身也来自网上收集，h3-comic-builder 只是中间层，不作为数据来源列出 |
| [willwulfken/MidJourney-Styles-and-Keywords-Reference](https://github.com/willwulfken/MidJourney-Styles-and-Keywords-Reference) (12.3k stars) | GitHub | 4,600 | composition, lighting, clothing, scene, styles |
| [Danbooru Tag Database](https://danbooru.donmai.us/wiki_pages/tag_groups) | 标签数据库 | 167 | character (发色/眼色/表情/服装/配件/姿势/特效) |
| Danbooru Booster Tags + [Civitai](https://civitai.com) 社区 | 社区收集 | 101 | quality (质量词/渲染技术/氛围/色彩/纹理) |
| Web 研究 — 场景与环境 | 手动整理 | 72 | scene (自然/建筑/天气/时间) |
| Web 研究 — 艺术风格 | 手动整理 | 41 | styles (绘画风格/动漫类型/美学流派/渲染技术) |
| [@nodaro/prompts](https://github.com/nodaroai/app.nodaro.ai) (v1.27.0) | GitHub | 1,149 | 23 个新分类 — 动作特效/美学微趋势/大气效果/镜头运动/姿态手势/转场效果等 |

**模板来源**：见 `templates/_meta.json` 的 `data_sources` 字段。

**每次数据更新的完整变更日志**：见 `keywords/_meta.json` 和 `templates/_meta.json` 的 `changelog` 字段。

---

*提示词仓库标准 v1.0 · 数据版本 v1.8.0 · 为漫画/手绘提示词生成而设计，适用于任何 AI 创意工具。*

*← [English](README_en.md)*
