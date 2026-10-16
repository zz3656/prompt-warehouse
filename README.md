# 提示词仓库标准（PWS）

**一个统一的、与语言无关的标准，用于跨项目组织、版本控制和共享 AI 生成提示词。**

> **pws v1.0.4** | **简体中文** | [English](README_en.md)
> **当前数据版本**: 1.0.4 (5,843 关键词 · 25 分类 · **1.9% 过时前缀** · 0 条校验失败)
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
- [分类体系](#-分类体系)
- [模板语法](#-模板语法)
- [配方包（Bundles）](#-配方包bundles)
- [工作流](#-工作流)
- [版本控制](#-版本控制)
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
| **结构化关键词** | 每个关键词都是富对象，带有元数据——评分、优先级、生命周期、使用统计 |
| **分类体系** | 25 个顶级分类及其嵌套子分类（质量、角色、服装、风格、镜头等） |
| **模板引擎** | 类 Mustache 语法，支持条件（`{{#if}}`）、迭代（`{{#each}}`）和辅助函数 |
| **配方包** | 预组合关键词配方，生成即开即用的提示词 |
| **工作流** | 多步骤模板组合，适用于 SD/Minimax H3 等 API |
| **静态 API** | `api/` 目录 — 供 GitHub Pages 部署后 HTTP 访问（stats, categories, bundles, workflows） |
| **迁移支持** | 内置从遗留 `.js` 文件迁移的路径 |
| **多语言** | 关键词和模板支持 EN / ZH 标签 |

---

## 📁 目录结构

```
prompt-warehouse/
├── schema/                     # JSON Schema 定义（机器可读）
│   ├── keyword.schema.json     # 关键词数据结构
│   ├── template.schema.json    # 模板数据结构
│   ├── bundle.schema.json      # 配方包结构
│   └── workflow.schema.json    # 工作流结构
├── keywords/                   # 关键词词典（"数据库"）
│   ├── _meta.json              # 全局元数据 + 版本信息
│   └── categories/             # 每个顶级分类一个文件
│       ├── quality.json        # 质量提升词
│       ├── camera.json         # 镜头/运镜（新）
│       ├── style.json          # 艺术风格（新）
│       ├── composition.json    # 构图 / 构图与镜头
│       ├── lighting.json       # 灯光与氛围
│       ├── character.json      # 角色外观属性
│       ├── clothing.json       # 服装与配饰
│       ├── styles.json         # 艺术风格（保留）
│       ├── animation.json      # 帧率/口型/运动模糊（新）
│       ├── storyboard.json     # 分镜布局/特效（新）
│       ├── negative.json       # 负面提示词
│       ├── scene.json          # 场景与环境
│       └── ...                 # 其余分类
├── bundles/                    # 配方包（Prompt Bundles）
│   └── *.json                  # 预组合关键词配方
├── workflows/                  # 工作流（多步骤模板组合）
│   └── *.json                  # 每个分类一个工作流
├── templates/                  # 模板定义
│   └── *.json
├── tools/                      # CLI 工具
│   ├── pws-translate.py        # 批量翻译
│   ├── pws-enrich.py           # 字段补全
│   ├── phase1-rename-mj-prefix.py  # 前缀清理
│   ├── phase2-new-categories.py    # 新分类创建
│   └── ...
└── docs/                       # 文档（精简后）
    ├── standard.md             # 完整标准文档
    ├── prompt-guide.md         # 使用指南
    └── adding-keywords.md      # 贡献指南
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
| `term` | string | ✅ | 标准提示词（英文），如 `masterpiece` |
| `term_zh` | string | ✅ | 中文翻译，如 `杰作` |
| `aliases` | string[] | | 英文替代术语，如 `["best work", "top tier"]` |
| `aliases_zh` | string[] | | 中文替代说法，如 `["最佳作品", "顶级"]` |
| `category` | string | ✅ | 顶级分类，共 25 类（见下方分类体系） |
| `subcategory` | string | ✅ | 子分类，如 `basic`, `hair`, `anime` |
| `labels` | string[] | | 英文扁平搜索标签 |
| `labels_zh` | string[] | | 中文扁平搜索标签 |
| `score` | number | | 质量评分 0–1（默认：0.5） |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` → `review` → `approved` → `deprecated` → `archived` |
| `source` | string | ✅ | 数据来源 |
| `score` | number | ✅ | 质量评分（100% 覆盖） |

### 分类体系

| 分类 | Slug | 说明 |
|------|------|------|
| 质量 | `quality` | AI 输出质量提升词 |
| 构图 | `composition` | 构图、角度、镜头效果 |
| 灯光 | `lighting` | 灯光类型与氛围 |
| 角色 | `character` | 角色外观属性 |
| 服装 | `clothing` | 服装与配饰 |
| 风格 | `styles` | 艺术与渲染风格（保留） |
| 风格 | `style` | **新分类**：从 styles 迁移的艺术风格 |
| 镜头 | `camera` | **新分类**：景别/镜头/运镜/角度 |
| 负面 | `negative` | 负面提示词 |
| 场景 | `scene` | 场景与环境 |
| 分镜 | `storyboard` | **新分类**：布局/特效/氛围 |
| 动画 | `animation` | **新分类**：帧率/口型/运动模糊 |
| 动作特效 | `action-fx` | 动作与特效 |
| 大气效果 | `atmosphere` | 雾、雨、粒子、神光 |
| 角色特效 | `character-fx` | 狼人、吸血鬼、赛博格等 |
| 色彩分级 | `color-look` | 暖色、冷色、胶片模拟 |
| 历史时代 | `era` | 中世纪、维多利亚、赛博朋克等 |
| 手持道具 | `held-prop` | 武器与道具 |
| 材质预设 | `material` | 织物、金属、石材、木材 |
| 摄影师风格 | `photographer` | Ansel Adams, Annie Leibovitz 等 |
| 镜头语言 | `shot-language` | 景别、角度、镜头运动 |
| 时间效果 | `temporal` | 慢动作、快速、时间冻结 |
| 转场效果 | `transitions` | 溶解、缩放、滑动 |

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

### 场景描述词

**户外场景：**

```
school rooftop at sunset, golden hour lighting, long shadows stretching across the ground, wind blowing through white hair, cherry blossom petals floating in the air, city skyline visible in the distance
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

## 📦 配方包（Bundles）

配方包是预组合的关键词 ID 列表，带有权重和模板引用，形成可复用的提示词配方。

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
| `character.animesque_portrait` | 24 | 动漫风格角色肖像 |
| `character.cosplay_portrait` | 20 | Cosplay 肖像 |
| `environment.architectural_interior` | 23 | 建筑室内可视化 |
| `environment.cityscape_exterior` | 22 | 城市景观 |
| `fashion.editorial_shoot` | 21 | 时尚编辑大片 |
| `food.editorial_style` | 21 | 美食编辑风格摄影 |
| `photography.cinematic_portrait` | 39 | 电影感人像配方 |
| `product.ecommerce_packshot` | 17 | 电商标准产品图 |
| `product.packaging_mockup` | 19 | 包装设计样机 |
| `scene.fantasy_landscape` | 26 | 奇幻风景配方 |

---

## 🔄 工作流

工作流是多步骤模板组合，适用于 SD/Minimax H3 等 API。每个工作流包含 `steps` 数组，定义执行顺序。

```json
{
  "id": "workflow.character_portrait",
  "name": "Character Portrait",
  "name_zh": "角色肖像",
  "steps": [
    { "order": 1, "template_id": "kw_1" },
    { "order": 2, "template_id": "kw_2" }
  ]
}
```

---

## 📦 版本控制

仓库遵循语义化版本控制：

| 类型 | 含义 |
|------|------|
| **主版本 (1.x.x)** | 结构变更，破坏性格式变更 |
| **次版本 (x.1.x)** | 新分类或字段，向后兼容 |
| **修订版 (x.x.1)** | 修复、数据修正、新增关键词 |

当前版本：**1.0.4** — 25 个分类共 5,843 个关键词。

### 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.1 | 2026-09-28 | 初始版本：22 分类，6,256 关键词 |
| 1.0.2 | 2026-10-12 | 自动生成 21 个工作流模板 (P7) |
| 1.0.3 | 2026-10-16 | Phase 1: 清理 mj_v5* 前缀，新增 camera/style/animation/storyboard |
| 1.0.4 | 2026-10-16 | Phase 3: 批量翻译 + aliases 补全 + 子分类规范化 |

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
| **阶段一：结构定义** | ✅ 完成 | 定义了 4 个 JSON Schema 并验证 |
| **阶段二：数据迁移** | ✅ 完成 | 从 h3-comic-builder + MJ 参考迁移了 ~6,000 个关键词 |
| **阶段三：工具开发** | ✅ 完成 | 15+ CLI 工具（索引、审计、翻译、去重、Bundle 管理等） |
| **阶段四：共享发布** | ✅ 完成 | 远程同步、配方包系统、工作流基础 |
| **阶段五：优化清理** | ✅ 完成 | 清理 mj_v5* 前缀（57%→1.9%），新增 4 个 AI 漫剧分类 |

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
- 遵循 `{category}_{subcategory}_{slug}` 的 id 命名规范（全小写，下划线分隔）
- 在设置 `lifecycle: "approved"` 之前，先用生成测试验证现有关键词

---

## 📄 许可证

MIT 许可证 — 详见 [docs/standard.md](docs/standard.md)。

---

## 📚 资源

- **完整规范**: [docs/standard.md](docs/standard.md)
- **使用指南**: [docs/prompt-guide.md](docs/prompt-guide.md)
- **贡献指南**: [docs/adding-keywords.md](docs/adding-keywords.md)
- **关键词结构**: [schema/keyword.schema.json](schema/keyword.schema.json)
- **模板结构**: [schema/template.schema.json](schema/template.schema.json)
- **Bundle 结构**: [schema/bundle.schema.json](schema/bundle.schema.json)
- **工作流结构**: [schema/workflow.schema.json](schema/workflow.schema.json)
- **管理工具**: [tools/pws-bundles.py](tools/pws-bundles.py)
- **元数据**: [keywords/_meta.json](keywords/_meta.json)

---

## 📥 数据来源（永久记录）

| 来源 | 类型 | 关键词数 | 涵盖分类 |
|------|------|----------|----------|
| h3-comic-builder 中间件 | *已迁移* | 859 | 全部 9 类 |
| [willwulfken/MidJourney-Styles-and-Keywords-Reference](https://github.com/willwulfken/MidJourney-Styles-and-Keywords-Reference) (12.3k stars) | GitHub | 4,600 | composition, lighting, clothing, scene, styles |
| [Danbooru Tag Database](https://danbooru.donmai.us/wiki_pages/tag_groups) | 标签数据库 | 167 | character (发色/眼色/表情/服装/配件/姿势/特效) |
| Danbooru Booster Tags + [Civitai](https://civitai.com) 社区 | 社区收集 | 101 | quality (质量词/渲染技术/氛围/色彩/纹理) |
| Web 研究 — 场景与环境 | 手动整理 | 72 | scene (自然/建筑/天气/时间) |
| Web 研究 — 艺术风格 | 手动整理 | 41 | styles (绘画风格/动漫类型/美学流派/渲染技术) |
| [@nodaro/prompts](https://github.com/nodaroai/app.nodaro.ai) (1.0.1) | GitHub | 1,149 | 23 个新分类 — 动作特效/美学微趋势/大气效果/镜头运动等 |

**每次数据更新的完整变更日志**：见 `keywords/_meta.json` 的 `changelog` 字段。

---

*提示词仓库标准 v1.0.4 · 数据版本 1.0.4 · 为漫画/手绘提示词生成而设计，适用于任何 AI 创意工具。*

*← [English](README_en.md)*
