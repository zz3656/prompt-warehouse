# 提示词仓库标准规范

> **pws v1.0** — 提示词仓库标准
>
> 一个统一的、与语言无关的标准，用于跨项目组织、版本控制和共享 AI 生成提示词。为漫画/手绘提示词生成而设计，适用于任何 AI 创意工具（图像、视频、文本、音乐）。
>
> **仓库地址**: https://github.com/[org]/prompt-warehouse
> **许可证**: MIT

---

## 1. 设计哲学

### 1.1 为什么需要这个标准？

当前的提示词管理存在以下问题：
- **数据孤岛**：每个项目都有自己的关键词文件、模板和数据模型
- **没有版本控制**：难以追踪哪个版本的提示词产生了什么结果
- **无法共享**：难以在不同项目之间复用优秀的提示词
- **缺乏结构化**：提示词是 JS 对象中的字符串，没有机器可读的结构
- **没有生命周期**：没有草稿/审核/批准/归档的概念

本标准通过以下方式解决这些问题：
1. 为所有提示词相关实体提供 **数据结构**
2. 提供人类可读且机器可解析的 **文件格式**（JSON）
3. 提供 **版本控制系统** 来追踪变更
4. 提供 **标签分类体系** 实现跨项目发现
5. 提供 **生命周期管理系统**（草稿 → 审核 → 批准 → 归档，含弃用状态）

### 1.2 范围

| 实体 | 说明 |
|------|------|
| `tag` | 提示词的基本构建块（单个关键词或短语） |
| `tag_category` | 标签分组（如"发色"、"灯光类型"） |
| `keyword` | 带有元数据的结构化标签（分类、子分类、标签、评分） |
| `template` | 带有变量占位符的可复用提示词模板 |
| `prompt` | 具体的提示词实例（模板渲染后的值） |
| `project` | 引用关键词和模板的应用级配置 |
| `snapshot` | 导出的提示词输出，包含使用上下文和结果 |

---

## 2. 目录结构

```
prompt-warehouse/
├── schema/                     # JSON Schema 定义（机器可读）
│   ├── keyword.schema.json
│   ├── template.schema.json
│   └── project.schema.json
├── keywords/                   # 关键词词典（"数据库"）
│   ├── _meta.json              # 全局元数据 + 版本信息
│   └── categories/             # 每个顶级分类一个文件
│       ├── quality.json
│       ├── composition.json
│       ├── lighting.json
│       ├── character.json
│       ├── clothing.json
│       ├── styles.json
│       ├── negative.json
│       ├── scene.json
│       └── panel.json
├── templates/                  # 提示词模板
│   ├── _meta.json
│   ├── character_sheet.json
│   ├── panel_prompt.json
│   └── reference_description.json
├── projects/                   # 项目配置
│   └── h3-comic-builder.json
├── snapshots/                  # 导出快照
│   └── YYYY/MM/
└── README_zh.md                # 本文件
```

---

## 3. 数据模型

### 3.1 关键词模型

每个关键词都是一个结构化对象：

```json
{
  "id": "qc_blonde_hair",
  "term": "blonde hair",
  "term_zh": "金发",
  "aliases": ["yellow hair", "golden hair"],
  "category": "character",
  "subcategory": "hairColors",
  "labels": ["hair", "color", "blonde", "platinum"],
  "score": 0.95,
  "priority": "high",
  "lifecycle": "approved",
  "tags": ["frequently-used", "anime"],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-06-20T14:30:00Z",
  "source": "prompt-engineering-wiki",
  "usage_count": 1247,
  "success_rate": 0.87,
  "notes": "与 SDXL 动漫模型配合良好。避免用于照片级真实场景。",
  "variations": [
    {"term": "platinum blonde hair", "context": "高价值角色"},
    {"term": "strawberry blonde hair", "context": "暖色灯光"}
  ]
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识符。格式：`{category}_{subcategory}_{slug}` |
| `term` | string | ✅ | 标准提示词（英文） |
| `term_zh` | string | | 中文翻译 |
| `aliases` | string[] | | 替代术语（非英文、口语化） |
| `category` | string | ✅ | 顶级分类（参见分类体系） |
| `subcategory` | string | ✅ | 分类内的子分类 |
| `labels` | string[] | | 扁平搜索标签（自动索引） |
| `score` | number | | 质量评分 0-1（默认：0.5） |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` / `review` / `approved` / `deprecated` / `archived` |
| `tags` | string[] | | 用户定义的标签，用于跨切面关注点 |
| `created_at` | iso-date | | ISO 8601 时间戳 |
| `updated_at` | iso-date | | ISO 8601 时间戳 |
| `source` | string | | 关键词来源（来源归属） |
| `usage_count` | number | | 使用次数（默认：0） |
| `success_rate` | number | | 生成成功率（0-1，默认：null） |
| `notes` | string | | 人类可读的备注 |
| `variations` | array | | 上下文相关的替代术语 |

#### 生命周期状态

```
草稿 → 审核 → 批准 → 归档
draft → review → approved → archived
              ↕           ↕
          (被拒绝)   (被弃用) ↗
          deprecated ↗
```

- **草稿 (draft)**：新添加，尚未验证
- **审核 (review)**：已提交审核，等待批准
- **批准 (approved)**：已验证，可用于生产
- **归档 (archived)**：不再使用，保留供参考
- **被弃用 (deprecated)**：正在逐步淘汰，由更新的替代方案取代

---

### 3.2 分类体系

```
quality           — AI 输出质量提升词
  ├── basic       — 标准质量标签
  ├── advanced    — 高端质量标签
  └── anime       — 动漫专用质量标签

composition       — 构图、角度、镜头效果
  ├── framing     — 镜头尺寸（特写、广角等）
  ├── angles      — 拍摄角度
  ├── lens        — 镜头类型和效果
  └── rules       — 构图规则

lighting          — 灯光类型与氛围
  ├── natural     — 自然光（阳光、黄金时段）
  ├── dramatic    — 戏剧/工作室灯光
  ├── mood        — 氛围灯光（冷色、霓虹等）
  ├── dynamic     — 动态大气效果
  └── special     — 特效（光晕、粒子）

character         — 角色外观属性
  ├── hair        — 发型和描述
  ├── hairColors  — 发色变体
  ├── eyes        — 眼睛描述
  ├── eyeColors   — 眼色变体
  ├── expression  — 面部表情
  ├── pose        — 身体姿势
  ├── anatomy     — 解剖描述
  ├── bodyType    — 体型
  └── skin        — 肤色

clothing          — 服装与配饰
  ├── tops        — 上半身服装
  ├── bottoms     — 下半身服装
  ├── outfits     — 完整套装
  └── accessories — 配饰和物品

styles            — 艺术与渲染风格
  ├── anime       — 动漫/漫画风格标签
  ├── art         — 通用艺术风格标签
  ├── realism     — 照片级真实标签
  ├── specialty   — 专业/小众风格
  └── artist      — 艺术家风格参考

negative          — 负面提示词
  ├── quality     — 质量负面词
  ├── anatomy     — 解剖失败
  ├── face        — 面部失败
  ├── composition — 构图失败
  ├── style       — 风格不匹配
  ├── text        — 文本相关负面
  └── defects     — 常见生成缺陷

scene             — 场景与环境
  ├── relationship — 角色关系
  ├── interaction — 角色互动
  ├── weather     — 天气条件
  └── time        — 时间段

panel             — 分镜特效
  ├── layout      — 分镜布局类型
  ├── effects     — 漫画/手绘视觉效果
  ├── animation   — 动画专用术语
  └── mood        — 分镜情感基调
```

---

### 3.3 模板模型

模板使用简单的 Mustache 风格语法，`<variable>` 占位符（与 CLI 一致）：

```json
{
  "id": "character.reference_description",
  "name": "Character Reference Description",
  "name_zh": "角色参考描述",
  "description": "用于分镜间角色一致性的紧凑角色描述",
  "category": "character",
  "subcategories": ["reference_description"],
  "language": "en",
  "api_targets": ["SDXL", "Midjourney", "DALL-E", "Flux"],
  "lifecycle": "approved",
  "score": 0.92,
  "tags": ["consistency", "character-sheet", "core"],
  "variables": [
    {"name": "gender", "type": "string", "required": true},
    {"name": "age", "type": "string", "required": false},
    {"name": "hair_color", "type": "string", "required": true},
    {"name": "hair_style", "type": "string", "required": false},
    {"name": "eye_color", "type": "string", "required": true},
    {"name": "skin_tone", "type": "string", "required": false},
    {"name": "distinctive_features", "type": "string[]", "required": false},
    {"name": "outfit_line", "type": "string", "required": false},
    {"name": "expression_line", "type": "string", "required": false}
  ],
  "variants": [
    {
      "id": "default",
      "description": "标准参考描述",
      "template": "{{gender}}{{#if age}} {{age}} years old{{/if}}{{#if hair_color}} {{hair_color}}{{#if hair_style}} {{hair_style}}{{/if}} hair{{/if}}{{#if eye_color}} {{eye_color}} eyes{{/if}}{{#if skin_tone}} {{skin_tone}} skin{{/if}}{{#each distinctive_features}}, {{this}}{{/each}}"
    },
    {
      "id": "minimal",
      "description": "简化版，用于 token 受限的模型",
      "template": "{{hair_color}} hair, {{eye_color}} eyes, {{skin_tone}} skin, {{gender}}{{#if age}}, {{age}}yo{{/if}}"
    }
  ],
  "examples": [
    {
      "input": {"gender": "girl", "age": "16", "hair_color": "white", "hair_style": "long", "eye_color": "blue", "skin_tone": "fair"},
      "output": "girl 16 years old white long hair blue eyes fair skin"
    }
  ],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-06-20T14:30:00Z",
  "notes": "核心一致性机制。同一角色的每个分镜提示词开头必须包含。"
}
```

---

### 3.4 项目配置模型

```json
{
  "id": "h3-comic-builder",
  "name": "H3 Comic Builder",
  "version": "1.0.0",
  "description": "AI 漫画/手绘提示词生成工具",
  "project_type": "comic",
  "prompt_warehouse_version": "1.0.0",
  "keywords": {
    "enabled_categories": ["quality", "composition", "lighting", "character", "clothing", "styles", "scene", "panel"],
    "excluded_categories": ["negative"],
    "custom_categories": ["comic_genre", "dialogue_style"]
  },
  "templates": {
    "enabled": ["character.reference_description", "panel.prompt", "character_sheet.full"],
    "custom": ["comic.panel.dialogue_overlay"]
  },
  "settings": {
    "default_api": "SDXL",
    "default_style": "anime",
    "max_prompt_length": 1500,
    "default_negative": "standard"
  },
  "custom_keywords_path": "keywords/custom",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-06-20T14:30:00Z"
}
```

---

### 3.5 快照模型

```json
{
  "id": "snap_20250620_143000_001",
  "project": "h3-comic-builder",
  "timestamp": "2025-06-20T14:30:00Z",
  "type": "export",
  "title": "第一章，第 1-5 格",
  "style": "anime",
  "api": "SDXL",
  "prompts": {
    "positive": "masterpiece, best quality, girl 16 years old white long hair blue eyes fair skin, medium shot, School Rooftop, golden hour, dialogue: Hello!",
    "negative": "low quality, worst quality, bad anatomy, extra limbs"
  },
  "context": {
    "chapter": 1,
    "panels": [1, 2, 3, 4, 5],
    "characters": ["yuki", "sora"],
    "locations": ["school_rooftop"]
  },
  "preview": "masterpiece, best quality, girl 16 years old white long hair...",
  "panels_count": 5,
  "characters_count": 2,
  "generation_results": null,
  "rating": null,
  "tags": ["chapter-1", "export"]
}
```

---

## 4. 迁移：JSON → PWS 结构

### 4.1 当前 h3-comic-builder 关键词文件

```
modules/
├── prompt_keywords_core.js      →  quality, composition, lighting
├── prompt_keywords_character.js →  character, clothing
└── prompt_keywords_scenes.js    →  styles, mood, scene, panel, negative
```

### 4.2 迁移映射

| 当前分类 | 文件 | PWS 分类文件 |
|---------|------|-------------|
| QUALITY | core.js | `keywords/categories/quality.json` |
| COMPOSITION | core.js | `keywords/categories/composition.json` |
| LIGHTING | core.js | `keywords/categories/lighting.json` |
| CHARACTER.* | character.js | `keywords/categories/character.json` |
| CLOTHING.* | character.js | `keywords/categories/clothing.json` |
| STYLES.* | scenes.js | `keywords/categories/styles.json` |
| NEGATIVE.* | scenes.js | `keywords/categories/negative.json` |
| SCENE.* | scenes.js | `keywords/categories/scene.json` |
| PANEL_SPECIFIC.* | scenes.js | `keywords/categories/panel.json` |

### 4.3 迁移脚本

迁移脚本（待实现）将：

1. 使用正则解析每个 `prompt_keywords_*.js` 文件
2. 将扁平数组转换为结构化关键词对象
3. 应用默认元数据（评分、生命周期、标签）
4. 生成符合 `{category}_{subcategory}_{slug}` 规范的 ID
5. 在 PWS 目录结构中输出 JSON 文件
6. 保留与现有 `.js` 文件的向后兼容性

---

## 5. 模板语法

### 5.1 变量

| 语法 | 说明 |
|------|------|
| `{{var}}` | 简单变量替换 |
| `{{obj.field}}` | 嵌套属性访问 |
| `{{array.0}}` | 数组索引访问 |

### 5.2 条件语句

| 语法 | 说明 |
|------|------|
| `{{#if var}}内容{{/if}}` | var 为真时渲染 |
| `{{#unless var}}内容{{/unless}}` | var 为假时渲染 |
| `{{#equals a 'b'}}内容{{/equals}}` | a 等于 b 时渲染 |
| `{{#notEquals a 'b'}}内容{{/notEquals}}` | a 不等于 b 时渲染 |
| `{{#between a 1 10}}内容{{/between}}` | a 在 1 到 10 之间时渲染 |

### 5.3 迭代

| 语法 | 说明 |
|------|------|
| `{{#each array}}item{{/each}}` | 遍历数组 |
| `{{#each obj}}key=value{{/each}}` | 遍历对象 |
| `{{@index}}` | 当前迭代索引 |
| `{{@key}}` | 对象迭代中的当前键 |
| `{{@first}}` | 布尔值：是否为第一项？ |
| `{{@last}}` | 布尔值：是否为最后一项？ |

### 5.4 辅助函数

| 辅助 | 用法 | 说明 |
|------|------|------|
| `join` | `{{join array ', '}}` | 用分隔符连接数组 |
| `length` | `{{length array}}` | 获取数组长度 |
| `escape` | `{{escape text}}` | HTML 转义文本 |
| `default` | `{{default var 'fallback'}}` | 默认值 |
| `upper` | `{{upper text}}` | 大写 |
| `lower` | `{{lower text}}` | 小写 |
| `trim` | `{{trim text}}` | 去除空白 |
| `truncate` | `{{truncate text 50}}` | 截断到 N 字符 |

### 5.5 迭代辅助函数（在 `each` 内）

| 辅助 | 用法 | 说明 |
|------|------|------|
| `@@index` | 在 `each` 内 | 当前 0 基索引 |
| `@@first` | 在 `each` 内 | 是否为第一项 |
| `@@last` | 在 `each` 内 | 是否为最后一项 |
| `@@key` | 对象 each | 当前键 |

---

## 6. 版本控制

### 6.1 文件版本

每个 `_meta.json` 文件包含：

```json
{
  "version": "1.0.0",
  "schema_version": "pws-1.0",
  "updated_at": "2025-06-20T14:30:00Z",
  "updated_by": "migration-script",
  "commit": "abc123"
}
```

### 6.2 递增规则

- **主版本 (1.x.x)**：结构变更，破坏性格式变更
- **次版本 (x.1.x)**：新分类或字段，向后兼容
- **修订版 (x.x.1)**：修复、数据修正、新增关键词

### 6.3 Git 集成

每次关键词/模板变更应包含：
- 遵循 conventional commits 格式的提交信息
- 仓库根目录的 `CHANGELOG.md` 条目
- 可选：分类目录中的 `review.md` 文件用于待变更

---

## 7. API 集成（REST）

PWS 标准设计用于与 h3-comic-builder 服务器这样的 REST API 配合使用：

### 关键词 API
```
GET    /api/keywords           列出关键词（分页、可筛选）
GET    /api/keywords/:id       获取关键词详情
POST   /api/keywords           创建关键词
PUT    /api/keywords/:id       更新关键词
DELETE /api/keywords/:id       删除关键词
GET    /api/keywords/search    全文搜索
GET    /api/keywords/stats     使用分析
POST   /api/keywords/import    批量导入（JSON/CSV）
GET    /api/keywords/export    完整导出
```

### 模板 API
```
GET    /api/templates              列出模板
GET    /api/templates/:id          获取模板
POST   /api/templates              创建模板
PUT    /api/templates/:id          更新模板
DELETE /api/templates/:id          删除模板
POST   /api/templates/:id/render   用数据渲染模板
```

### 快照 API
```
GET    /api/snapshots              列出快照
GET    /api/snapshots/:id          获取快照
POST   /api/snapshots              导入/创建快照
DELETE /api/snapshots/:id          删除快照
```

---

## 8. 多语言支持

### 8.1 关键词标签

关键词支持多语言标签：

```json
{
  "id": "qc_graceful_lighting",
  "term": "beautiful lighting",
  "term_zh": "美丽的光线",
  "labels": ["lighting", "glow", "illumination"],
  "labels_zh": ["灯光", "光影", "光线", "美丽"],
  "labels_ja": ["照明", "光", "影", "美しい"],
  "term_ja": "美しい照明"
}
```

### 8.2 模板语言

模板可以有特定语言的变体：

```json
{
  "variants": [
    {"id": "en", "template": "{{variable}}", "language": "en"},
    {"id": "zh", "template": "{{variable}}", "language": "zh"},
    {"id": "ja", "template": "{{variable}}", "language": "ja"}
  ]
}
```

---

## 9. 示例：转换当前数据

### 之前（prompt_keywords_core.js）：
```javascript
var QUALITY = {
  basic: [
    'masterpiece', 'best quality', 'high quality', 'high resolution'
  ]
};
```

### 之后（keywords/categories/quality.json）：
```json
[
  {
    "id": "qc_basic_masterpiece",
    "term": "masterpiece",
    "term_zh": "杰作",
    "category": "quality",
    "subcategory": "basic",
    "labels": ["quality", "booster", "masterpiece"],
    "score": 0.99,
    "priority": "high",
    "lifecycle": "approved",
    "tags": ["frequently-used", "universal"],
    "usage_count": 45230,
    "success_rate": 0.94
  },
  {
    "id": "qc_basic_best_quality",
    "term": "best quality",
    "term_zh": "最高质量",
    "category": "quality",
    "subcategory": "basic",
    "labels": ["quality", "booster", "best"],
    "score": 0.99,
    "priority": "high",
    "lifecycle": "approved",
    "tags": ["frequently-used", "universal"],
    "usage_count": 43180,
    "success_rate": 0.93
  },
  ...
]
```

---

## 10. 采用指南

### 阶段一：结构定义（当前）
- [x] 定义数据模型（关键词、模板、项目、快照）
- [x] 创建 JSON Schema 文件用于验证
- [x] 记录标准文档

### 阶段二：迁移
- [ ] 创建从 `.js` 文件到 JSON 的迁移脚本
- [ ] 在 h3-comic-builder 数据上运行迁移
- [ ] 验证所有约 350 个关键词都已保留
- [ ] 更新管理后台以提供 JSON 而非解析 `.js` 文件

### 阶段三：工具开发
- [ ] 仓库管理的 CLI 工具（`pws`）
- [ ] 关键词管理的 Web UI（扩展现有管理后台）
- [ ] 搜索和分析仪表板
- [ ] 导入/导出工具（CSV、Excel、JSON）

### 阶段四：共享
- [ ] 远程仓库同步
- [ ] 团队协作功能
- [ ] 提示词评分和反馈
- [ ] 模板市场

---

## 附录 A：分类参考

| 分类 | Slug | 默认评分 | 生命周期 |
|------|------|----------|----------|
| 质量 | `quality` | 0.85 | approved |
| 构图 | `composition` | 0.75 | approved |
| 灯光 | `lighting` | 0.80 | approved |
| 角色 | `character` | 0.70 | approved |
| 服装 | `clothing` | 0.65 | approved |
| 风格 | `styles` | 0.75 | approved |
| 负面 | `negative` | 0.90 | approved |
| 场景 | `scene` | 0.60 | approved |
| 分镜 | `panel` | 0.65 | approved |

## 附录 B：评分解读

| 评分范围 | 含义 |
|----------|------|
| 0.90 - 1.00 | 经过验证，行业标准，几乎总是有效 |
| 0.70 - 0.89 | 可靠，常用，效果好 |
| 0.50 - 0.69 | 情境有用，依赖模型 |
| 0.30 - 0.49 | 实验性，小众，低置信度 |
| 0.00 - 0.29 | 未验证，需要测试 |

## 附录 C：未来扩展

- **提示词链**：将多个模板连接为管道
- **A/B 测试**：追踪哪些关键词表现更好
- **模型特定变体**：SDXL vs MJ vs DALL-E 的不同版本
- **提示词对比**：可视化比较不同提示词版本
- **提示词对话**：自然语言查询："显示所有夜间场景的灯光关键词"
- **提示词查重**：检测两个提示词是否过于相似

---

*← [English version](STANDARD_en.md)*
