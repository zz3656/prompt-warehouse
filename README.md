# 提示词仓库标准（PWS）

**一个统一的、与语言无关的标准，用于跨项目组织、版本控制和共享 AI 生成提示词。**

> **pws v1.0** | **简体中文** | [English](README_en.md)
>
> **仓库地址**: https://github.com/[org]/prompt-warehouse
> **许可证**: MIT

---

## 📖 目录

- [概述](#-概述)
- [功能](#-功能)
- [目录结构](#-目录结构)
- [快速开始](#-快速开始)
- [数据模型](#-数据模型)
- [模板语法](#-模板语法)
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
└── STANDARD_zh.md              # 完整标准文档
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

模板支持变量替换。`_all_templates.json` 文件包含所有 24 个模板的完整元数据：

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
| `id` | string | ✅ | 唯一标识符。格式：`{category}_{subcategory}_{slug}` |
| `term` | string | ✅ | 标准提示词（英文） |
| `term_zh` | string | | 中文翻译 |
| `category` | string | ✅ | 顶级分类 |
| `subcategory` | string | ✅ | 子分类 |
| `score` | number | | 质量评分 0–1（默认：0.5） |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` → `review` → `approved` → `archived` |

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

### 子分类亮点

**质量** — `basic` · `advanced` · `anime`
> 杰作 · 最高质量 · 超细节

**角色** — `hair` · `hairColors` · `eyes` · `eyeColors` · `expression` · `pose` · `anatomy` · `bodyType` · `skin`
> 白色长发 · 蓝眼睛 · 白皙皮肤 · 坚定的表情

**服装** — `tops` · `bottoms` · `outfits` · `accessories`
> 校服 · 白衬衫 · 百褶裙 · 红丝带

**风格** — `anime` · `art` · `realism` · `specialty` · `artist`
> 动漫风格 · 赛璐珞上色 · 漫画风格

**负面** — `quality` · `anatomy` · `face` · `composition` · `style` · `text` · `defects`
> 低质量 · 最差质量 · 畸形解剖 · 多余肢体

**灯光** — `natural` · `dramatic` · `mood` · `dynamic` · `special`
> 黄金时段 · 电影灯光 · 体积光

### 生命周期状态

```
草稿 → 审核 → 批准 → 归档
draft → review → approved → archived
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

当前版本：**v1.0.2** — 9 个分类共 4,429 个关键词。

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
| **阶段二：数据迁移** | ✅ 完成 | 从 h3-comic-builder + MJ 参考迁移了 4,429 个关键词 |
| **阶段三：工具开发** | 🔄 进行中 | 浏览器界面的关键词管理 |
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

MIT 许可证 — 详见 [STANDARD_zh.md](STANDARD_zh.md)。

---

## 📚 资源

- **完整规范**: [STANDARD_zh.md](STANDARD_zh.md)
- **关键词结构**: [schema/keyword.schema.json](schema/keyword.schema.json)
- **模板结构**: [schema/template.schema.json](schema/template.schema.json)
- **项目结构**: [schema/project.schema.json](schema/project.schema.json)
- **元数据**: [keywords/_meta.json](keywords/_meta.json)
- **当前统计**: 4,429 个关键词 · 9 个分类 · 24 个模板

---

*提示词仓库标准 v1.0 · 为漫画/手绘提示词生成而设计，适用于任何 AI 创意工具。*

*← [English](README_en.md)*
