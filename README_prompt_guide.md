# 提示词使用指南

> **Prompt Usage Guide** — 提示词仓库标准使用指南
>
> **仓库地址**: https://github.com/zz3656/prompt-warehouse

---

## 目录

1. [快速开始](#快速开始)
2. [图像生成提示词](#图像生成提示词)
3. [视频生成提示词](#视频生成提示词)
4. [LLM 文本生成提示词](#llm-文本生成提示词)
5. [漫画/分镜提示词](#漫画分镜提示词)
6. [提示词组合公式](#提示词组合公式)
7. [平台特定优化](#平台特定优化)

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

### 质量词分层使用

| 层级 | 关键词 | 适用场景 |
|------|--------|----------|
| 基础 | `masterpiece`, `best quality`, `high quality`, `high resolution` | 所有图像生成 |
| 进阶 | `professional`, `award winning`, `trending on artstation`, `intricate details` | 追求更高品质 |
| 动漫 | `official art`, `key visual`, `anime screencap`, `clean lineart` | 动漫/漫画风格 |

---

## 图像生成提示词

### 1. 角色设计

```
完整角色描述公式：
[数量] + [性别/年龄] + [发型发色] + [眼色] + [肤色] + [服装] + [表情] + [姿势]

示例：
1girl, 16 years old, white long hair, blue eyes, fair skin, 
wearing white shirt and blue pleated skirt, gentle smile, standing pose,
high quality, detailed face
```

**常用发色关键词：**
- `black hair`, `brown hair`, `blonde hair`, `red hair`
- `blue hair`, `pink hair`, `green hair`, `silver hair`
- `gradient hair`, `two-tone hair`, `highlighted hair`

**常用表情关键词：**
- `smiling`, `smirk`, `blushing`, `serious expression`
- `surprised expression`, `angry expression`, `winking`
- `tears`, `fangs`, `derpy expression`

### 2. 场景与环境

```
场景描述公式：
[地点类型] + [天气/时间] + [环境细节] + [氛围词]

示例：
cherry blossom trees, spring season, soft pink petals falling,
golden hour, atmospheric, serene
```

**常用场景分类：**

| 自然 | 建筑 | 天气/时间 |
|------|------|-----------|
| `forest`, `mountain`, `beach` | `castle`, `temple`, `library` | `sunset`, `rainy`, `snowy` |
| `waterfall`, `river`, `lake` | `cafe`, `school`, `lab` | `starry sky`, `aurora`, `twilight` |
| `desert`, `canyon`, `meadow` | `bridge`, `lighthouse`, `greenhouse` | `foggy`, `misty`, `clear sky` |

### 3. 灯光与氛围

```
灯光公式：
[光源类型] + [光线方向] + [氛围效果]

示例：
golden hour lighting, warm sunset glow, backlit rim light,
atmospheric fog, cinematic look
```

**常用灯光：**
- `golden hour`, `blue hour`, `moonlight`
- `volumetric lighting`, `god rays`, `rim lighting`
- `cinematic lighting`, `moody lighting`, `soft lighting`
- `dramatic side lighting`, `chiaroscuro`

### 4. 构图与镜头

```
镜头公式：
[景别] + [角度] + [镜头效果]

示例：
medium shot, eye level, shallow depth of field, bokeh background
```

**常用景别：**

| 景别 | 描述 | 英文关键词 |
|------|------|-----------|
| 极特写 | 面部/局部 | `extreme close-up`, `close-up` |
| 特写 | 头部和肩部 | `portrait`, `close-up` |
| 中景 | 腰部以上 | `medium shot`, `cowboy shot` |
| 全景 | 全身 | `full body`, `wide shot` |
| 远景 | 环境全貌 | `extreme wide`, `establishing shot` |

**常用角度：**
- `low angle shot` (仰视), `high angle shot` (俯视)
- `dutch angle` (倾斜), `over the shoulder` (过肩)
- `from behind` (背面), `three-quarter view` (四分之三)

### 5. 负面提示词

```
负面提示词公式：
[质量负面] + [解剖负面] + [面部负面] + [风格负面]

标准负面：
low quality, worst quality, bad anatomy, extra limbs, 
extra fingers, fewer fingers, cropped, watermark, text,
ugly, deformed, noisy, blurry
```

**更完整的负面词：**

| 类别 | 关键词 |
|------|--------|
| 质量 | `low quality`, `worst quality`, ` JPEG artifacts` |
| 解剖 | `bad anatomy`, `bad proportions`, `extra limbs`, `missing limbs` |
| 面部 | `bad face`, `deformed face`, `crossed eyes`, `mutation` |
| 构图 | `cropped`, `out of frame`, `cut off`, `duplicate` |
| 风格 | `3d`, `disney`, `realistic`, `photorealistic` (动漫时) |

---

## 视频生成提示词

### H3 (Minimax) 视频提示词

```
视频公式：
[主体+动作] + [场景] + [镜头运动] + [灯光] + [氛围] + --motion N --stability M

参数：
--motion 1-10 (1=静态, 10=动态最大)
--stability 1-10 (10=最稳定)
```

### 常用镜头运动模板

**慢推镜头（情感时刻）：**
```
Slow push-in from medium shot to close-up on [主体], [动作] in [场景],
lighting gradually shifts as emotion builds, shallow depth of field,
cinematic character moment, --motion 2 --stability 7
```

**环绕镜头（展示细节）：**
```
Camera slowly orbits around [主体] 360 degrees, [动作] in [场景],
soft diffused lighting, floating dust particles, ethereal atmosphere,
--motion 2 --stability 8
```

**航拍镜头（宏大场景）：**
```
Top-down aerial view, camera rotates slowly above [主体] in [场景],
overhead lighting creates geometric shadows, cinematic scale,
--motion 3 --stability 7
```

**希区柯克变焦（紧张感）：**
```
Dolly zoom, camera tracks backward while zooming in on [主体] in [场景],
background distorts, dramatic chiaroscuro lighting,
cinematic horror look, --motion 5 --stability 4
```

### 视频风格预设

| 场景类型 | motion | stability | 说明 |
|----------|--------|-----------|------|
| 静态肖像 | 1 | 9 | 最小运动，最稳定 |
| 对话场景 | 3 | 7 | 微妙的头部动作 |
| 情感特写 | 2 | 7 | 缓慢推进/拉远 |
| 漫步场景 | 4 | 6 | 中等运动 |
| 追逐/动作 | 8 | 3 | 高动态 |
| 爆炸/特效 | 9 | 2 | 最大动态 |

---

## LLM 文本生成提示词

### 系统提示词选择

| 用途 | 系统提示词变体 | 来源 |
|------|---------------|------|
| 代码助手 | `code-assistant` | GitHub Copilot 最佳实践 |
| 创意写作 | `creative-writer` | NovelAI / 写作社区 |
| 数据分析 | `data-analyst` | 数据科学社区 |
| 学术研究 | `research-assistant` | 学术写作指南 |
| 角色扮演 | `role-play` | TTRPG / 互动小说 |
| 产品管理 | `product-manager` | PM 社区最佳实践 |
| 安全审计 | `security-auditor` | OWASP / 安全社区 |
| 教学解释 | `teacher` | 教育学最佳实践 |

### 负面约束（Anti-Patterns）

在系统提示中加入以下约束可显著提升输出质量：

```
避免：
1. 幻觉：不要编造事实、引用或细节
2. 重复：避免重复相同的想法或句式
3. 冗长：不要过度解释简单问题
4. 对话填充：避免 "Great question!" "I'd be happy to help!"
5. 偏见：避免性别、文化、年龄等刻板印象
6. 结构混乱：确保格式一致、层次清晰
```

---

## 漫画/分镜提示词

### 角色一致性

确保同一角色在不同画面中保持一致：

```
每格提示词开头添加：
[性别][年龄][发色][发型][眼色][肤色][特征细节]

示例：
girl 16 years old white long hair blue eyes fair skin, freckles,
standing pose, school uniform, determined expression
```

### 分镜镜头语言

| 镜头 | 适用场景 | 关键词 |
|------|----------|--------|
| 特写 | 情感表达、细节展示 | `extreme close-up`, `close-up` |
| 过肩 | 对话、交流 | `over the shoulder` |
| 低角度 | 英雄登场、力量感 | `low angle shot`, `hero shot` |
| 俯角 | 弱势、孤独感 | `high angle shot` |
| 广角 | 环境展示、冲击 | `wide shot`, `fisheye` |
| 倾斜 | 紧张、不安、动感 | `dutch angle` |

### 漫画特效词

| 效果 | 关键词 |
|------|--------|
| 速度线 | `speed lines`, `motion lines`, `action lines` |
| 闪光 | `flash`, `light burst`, `sparkle` |
| 汗滴 | `sweat drop`, `perspiration` |
| 青筋 | `forehead vein`, `anger vein` |
| 气泡 | `thought bubble`, `speech bubble` |
| 等比例放大 | `powerful aura`, `intimidating` |

---

## 提示词组合公式

### 通用提示词模板

```json
{
  "quality": "masterpiece, best quality, highly detailed",
  "subject": "1girl, white long hair, blue eyes, fair skin",
  "outfit": "wearing white shirt and blue pleated skirt",
  "expression": "gentle smile, blushing",
  "pose": "standing pose, hand on hip",
  "background": "school rooftop, cherry blossom trees",
  "time": "golden hour, warm sunset",
  "lighting": "rim lighting, atmospheric fog",
  "composition": "medium shot, eye level, shallow depth of field",
  "style": "anime style, official art"
}
```

### 提示词权重语法

```
# Stable Diffusion 风格
常用词(1.1) 或 非常用词:1.2

# Midjourney 风格
--iw 2 (图片权重)
--s 100 (风格强度)
--c 5 (创意程度)

# 通用比例语法
词:权重 或 (词:权重)
```

### 高质量组合示例

**动漫角色：**
```
masterpiece, best quality, 1girl, white long hair, blue eyes, 
wearing school uniform, standing on rooftop at sunset,
cherry blossom petals falling, golden hour lighting, 
shallow depth of field, bokeh, anime style, official art, 
beautiful lighting
```

**写实人像：**
```
masterpiece, best quality, 1girl, 8k uhd, highly detailed,
photograph, RAW photo, detailed eyes, realistic skin texture, 
porcelain skin, soft lighting, shallow depth of field, 
portrait, looking at viewer, gentle smile
```

**场景风光：**
```
masterpiece, best quality, mountain range with cherry blossom trees, 
golden hour lighting, atmospheric fog, volumetric lighting,
dramatic sky, clouds, cinematic look, wide shot, 
beautiful composition, 8k uhd
```

---

## 平台特定优化

### Stable Diffusion / SDXL

- 使用 Danbooru 标签体系
- 质量词放开头：`masterpiece, best quality,`
- 负面提示词必须搭配使用
- 权重语法：`(word:1.2)` 或 `word:1.2`
- 推荐模型：AbyssOrangeMix3 (anime), JuggernautXL (realistic)

### Midjourney

- 自然语言提示词效果更好
- 使用 `--v 6` 或 `--niji 6`（动漫模式）
- 常用参数：`--ar 16:9`, `--stylize 100`, `--chaos 10`
- 图片参考：`--sref [url]`
- 角色一致性：使用种子控制 `--seed 1234`

### Flux

- 详细自然语言描述效果最佳
- 字数不限，越详细越好
- 支持复杂场景和多角色
- 推荐：Flux.1 Schnell, Flux.1 Pro

### DALL-E 3

- 对话式提示词效果更好
- 可以直接对话修正
- 适合复杂场景和文本生成
- 不支持负面提示词

### Minimax H3（视频）

- 镜头运动描述要具体
- 使用 `--motion` 和 `--stability` 参数
- 场景描述包含时间、天气、光线
- 动作描述要连贯、有时序感

---

## 参考资料

- **Danbooru 标签库**: https://danbooru.donmai.us/wiki_pages/tag_groups
- **Midjourney Styles and Keywords**: https://github.com/willwulfken/MidJourney-Styles-and-Keywords-Reference
- **BetaDoggo Danbooru Tag List**: https://github.com/BetaDoggo/danbooru-tag-list
- **NovelAI Prompting Guide**: https://docs.novelai.net/en/image/tutorial-characterCreation
- **Prompt Engineering Guide**: https://www.promptingguide.ai
- **Civitai 社区**: https://civitai.com

---

*← [English](README_en.md) | [中文](README_zh.md) | [标准规范](STANDARD.md)*
