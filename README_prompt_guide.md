# 提示词使用指南

> **Prompt Usage Guide** — 面向实际使用的提示词组合与优化建议
>
> **仓库地址**: https://github.com/zz3656/prompt-warehouse
>
> **完整数据模型与字段说明**：[README.md](README.md) | [STANDARD.md](STANDARD.md)

---

## 快速开始

### 提示词基本结构

```
[质量词] + [主体描述] + [场景/环境] + [构图/镜头] + [灯光/氛围] + [风格]
```

**示例：**
```
masterpiece, best quality, 1girl, white long hair, blue eyes, standing on school rooftop, medium shot, golden hour lighting, anime style
```

### 质量词分层

| 层级 | 关键词 | 适用场景 |
|------|--------|----------|
| 基础 | `masterpiece`, `best quality`, `high quality`, `high resolution` | 所有图像生成 |
| 进阶 | `professional`, `award winning`, `trending on artstation` | 追求更高品质 |
| 动漫 | `official art`, `key visual`, `anime screencap` | 动漫/漫画风格 |

> 完整关键词库在 `keywords/categories/` 下，按分类文件浏览。

---

## 图像生成提示词

### 角色设计

```
[数量] + [性别/年龄] + [发型发色] + [眼色] + [肤色] + [服装] + [表情] + [姿势]
```

常用发色：`black hair`, `blonde hair`, `white hair`, `red hair`, `blue hair`, `pink hair`, `silver hair`
常用表情：`smiling`, `smirk`, `blushing`, `serious`, `surprised`, `angry`, `winking`

> 完整列表见 `keywords/categories/character.json`（角色）和 `clothing.json`（服装）。

### 场景与环境

```
[地点类型] + [天气/时间] + [环境细节] + [氛围词]
```

常用场景分类：

| 自然 | 建筑 | 天气/时间 |
|------|------|-----------|
| `forest`, `mountain`, `beach` | `castle`, `temple`, `cafe` | `sunset`, `rainy`, `snowy` |
| `waterfall`, `river`, `desert` | `library`, `school`, `bridge` | `starry sky`, `aurora`, `foggy` |

> 见 `keywords/categories/scene.json` 和 `setting.json`。

### 灯光与氛围

```
[光源类型] + [光线方向] + [氛围效果]
```

常用灯光：`golden hour`, `blue hour`, `moonlight`, `volumetric lighting`, `rim lighting`, `cinematic lighting`, `chiaroscuro`

> 见 `keywords/categories/lighting.json`。

### 构图与镜头

| 景别 | 关键词 |
|------|--------|
| 极特写 | `extreme close-up` |
| 特写 | `portrait`, `close-up` |
| 中景 | `medium shot`, `cowboy shot` |
| 全景 | `full body`, `wide shot` |
| 远景 | `extreme wide`, `establishing shot` |

常用角度：`low angle`（仰视）, `high angle`（俯视）, `dutch angle`（倾斜）, `over the shoulder`（过肩）

> 见 `keywords/categories/composition.json` 和 `framing.json`。

### 负面提示词

标准负面：
```
low quality, worst quality, bad anatomy, extra limbs, extra fingers,
fewer fingers, cropped, watermark, text, ugly, deformed, noisy, blurry
```

> 完整负面词列表见 `keywords/categories/negative.json`。

---

## 视频生成提示词（Minimax H3）

```
[主体+动作] + [场景] + [镜头运动] + [灯光] + [氛围] + --motion N --stability M

--motion 1-10（1=静态, 10=动态最大）
--stability 1-10（10=最稳定）
```

### 场景-参数推荐

| 场景类型 | motion | stability | 说明 |
|----------|--------|-----------|------|
| 静态肖像 | 1 | 9 | 最小运动 |
| 对话场景 | 3 | 7 | 微妙头部动作 |
| 情感特写 | 2 | 7 | 缓慢推进/拉远 |
| 漫步 | 4 | 6 | 中等运动 |
| 追逐/动作 | 8 | 3 | 高动态 |
| 爆炸/特效 | 9 | 2 | 最大动态 |

> 完整视频模板见 `templates/h3_video_prompts.json`。

---

## LLM 文本生成提示词

### 系统提示词

| 用途 | 变体 ID |
|------|---------|
| 代码助手 | `code-assistant` |
| 创意写作 | `creative-writer` |
| 数据分析 | `data-analyst` |
| 学术研究 | `research-assistant` |
| 角色扮演 | `role-play` |
| 产品管理 | `product-manager` |
| 安全审计 | `security-auditor` |
| 教学 | `teacher` |

### 负面约束（Anti-Patterns）

在系统提示中加入约束可显著提升输出质量：
1. 幻觉：不要编造事实或引用
2. 重复：避免重复相同想法
3. 冗长：不要过度解释
4. 对话填充：避免 "Great question!"
5. 偏见：避免性别/文化刻板印象

> 完整模板见 `templates/llm_system_prompts.json`。

---

## 漫画/分镜提示词

### 角色一致性

```
每格提示词开头添加：
[性别][年龄][发色][发型][眼色][肤色][特征细节]
```

### 分镜镜头语言

| 镜头 | 适用场景 | 关键词 |
|------|----------|--------|
| 特写 | 情感表达 | `extreme close-up` |
| 过肩 | 对话 | `over the shoulder` |
| 低角度 | 英雄登场 | `low angle shot`, `hero shot` |
| 广角 | 环境展示 | `wide shot`, `fisheye` |
| 倾斜 | 紧张感 | `dutch angle` |

> 完整分镜模板见 `templates/_all_templates.json`。

---

## 提示词组合公式

### 权重语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `(word)` | 提高权重 | `(masterpiece:1.2)` |
| `[word]` | 降低权重 | `[low quality]` |
| `word:1.5` | SD 风格权重 | `white hair:1.3` |

### 高质量组合示例

**动漫角色半身像：**
```
(masterpiece:1.2), (best quality:1.2), 1girl, (white long hair:1.2), blue eyes,
fair skin, school uniform, gentle smile, medium shot, rule of thirds,
golden hour lighting, soft bokeh background, anime style
```

**户外战斗场景：**
```
(masterpiece:1.2), (award winning:1.2), 1girl, red hair, determined expression,
dynamic action pose, punch forward, motion blur, debris flying,
low angle shot, dramatic side lighting, cinematic composition,
dark clouds, lightning, battle scene
```

---

## 平台特定优化

### Stable Diffusion / SDXL
- 使用 `(word:1.2)` 语法提高权重
- 负面提示词必须：`low quality, worst quality, bad anatomy, extra limbs`
- 推荐分辩率：1024×1024

### Midjourney
- 使用 `/imagine prompt:` 开头
- 参数：`--ar 16:9`, `--v 6.0`, `--style raw`
- 质量词放在最前面

### Flux
- 支持自然语言描述
- 减少质量词权重，增强场景描述
- 适合生成写实图像

### DALL-E 3
- 使用完整自然语言句子
- 包含明确的场景和风格描述
- 不适合精确的角色一致性

### Minimax H3（视频）
- 使用 `--motion` 和 `--stability` 参数
- 避免过多质量词（消耗 token）
- 重点描述主体动作和镜头运动

---

## 参考

- **关键词词典**：`keywords/categories/` — 33 个分类，5,959 个关键词
- **模板**：`templates/` — 27 个模板
- **数据模型**：[README.md](README.md) | [STANDARD.md](STANDARD.md)
- **JSON Schema**：`schema/`
- **补充指南（含去重）**：[ADD_PROMPTS_GUIDE.md](ADD_PROMPTS_GUIDE.md)
