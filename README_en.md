# Prompt Warehouse Standard (PWS)

**A unified, language-agnostic standard for organizing, versioning, and sharing AI generation prompts across projects.**

> **pws v1.0** | [简体中文](README_zh.md) | **English**
>
> **Repository**: https://github.com/[org]/prompt-warehouse
> **License**: MIT

---

# Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Directory Structure](#-directory-structure)
- [Quick Start](#-quick-start)
- [Data Models](#-data-models)
- [Template Syntax](#-template-syntax)
- [Versioning](#-versioning)
- [API Integration](#-api-integration)
- [Multi-Language Support](#-multi-language-support)
- [Project Status](#-project-status)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The Prompt Warehouse Standard (PWS) is a JSON-based specification for managing AI generation prompts. It solves common problems:

- **No more silos**: Share keywords and templates across all your AI projects (image, video, text, music)
- **Version control**: Track which version of a prompt produced what result
- **Structured data**: Machine-readable JSON with full metadata (scores, lifecycle, usage analytics)
- **Cross-project discovery**: Tag-based taxonomy lets you find the right keyword instantly
- **Lifecycle management**: Draft → Review → Approved → Archived pipeline

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Structured Keywords** | Every keyword is a rich object with metadata — score, priority, lifecycle, usage stats |
| **Category Taxonomy** | 9 top-level categories with nested subcategories (quality, character, clothing, styles, etc.) |
| **Template Engine** | Mustache-like syntax with conditionals (`{{#if}}`), iteration (`{{#each}}`), and helpers |
| **Project Configs** | Per-project JSON configs that enable/disable categories and templates |
| **Snapshot System** | Export snapshots with full context for tracking generations |
| **Migration Ready** | Built-in migration path from legacy `.js` files |
| **Multi-Language** | Keywords and templates support EN / ZH / JA labels |

---

## 📁 Directory Structure

```
prompt-warehouse/
├── schema/                     # JSON Schema definitions (machine-readable)
│   ├── keyword.schema.json     # Keyword data structure
│   ├── template.schema.json    # Template data structure
│   └── project.schema.json     # Project config structure
├── keywords/                   # Keyword dictionary ("database")
│   ├── _meta.json              # Global metadata + version info
│   └── categories/             # One file per top-level category
│       ├── quality.json        # Quality boosters
│       ├── composition.json    # Composition & camera
│       ├── lighting.json       # Lighting & atmosphere
│       ├── character.json      # Character physical attributes
│       ├── clothing.json       # Clothing & accessories
│       ├── styles.json         # Art styles
│       ├── negative.json       # Negative prompts
│       ├── scene.json          # Scene & environment
│       └── panel.json          # Panel-specific effects
├── templates/                  # Prompt templates
│   ├── _meta.json              # Template metadata
│   └── _all_templates.json     # All templates (raw data)
├── projects/                   # Project configs
│   └── h3-comic-builder.json   # H3 Comic Builder config
├── snapshots/                  # Export snapshots
│   └── YYYY/MM/
└── STANDARD_en.md              # Full specification
```

---

## 🚀 Quick Start

### 1. Browse Keywords

Each category file is a plain JSON array. Open any file to explore:

```bash
# View all quality keywords
cat keywords/categories/quality.json | head -50

# Search for a specific term
grep -r '"term": "blonde hair"' keywords/categories/character.json
```

### 2. Use Templates

Templates support variable substitution. The `_all_templates.json` file contains all 24 templates with full metadata:

```json
// Character reference description template
{
  "id": "character.reference_description",
  "name": "Character Reference Description",
  "name_zh": "角色参考描述",
  "variables": ["gender", "age", "hair_color", "hair_style", "eye_color", "skin_tone"],
  "example_output": "girl 16 years old white long hair blue eyes fair skin"
}
```

### 3. Configure a Project

Edit a project config to enable/disable categories and templates:

```bash
cat projects/h3-comic-builder.json
```

---

## 🗂️ Data Models

### Keyword Model

Every keyword is a structured JSON object with rich metadata:

```json
{
  "id": "qc_graceful_lighting",
  "term": "graceful lighting",
  "aliases": ["beautiful lighting", "elegant lighting"],
  "category": "quality",
  "subcategory": "lighting",
  "labels": ["lighting", "glow", "illumination"],
  "score": 0.92,
  "priority": "high",
  "lifecycle": "approved",
  "tags": ["frequently-used", "universal"],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-06-20T14:30:00Z",
  "source": "h3-comic-builder-migration",
  "usage_count": 1247,
  "success_rate": 0.87,
  "notes": "Works well with SDXL anime models.",
  "variations": [
    {"term": "beautiful lighting", "context": "portrait scenes"}
  ]
}
```

### Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique ID. Format: `{category}_{subcategory}_{slug}` |
| `term` | string | ✅ | Canonical prompt term (English) |
| `category` | string | ✅ | Top-level category |
| `subcategory` | string | ✅ | Sub-category |
| `score` | number | | Quality score 0–1 (default: 0.5) |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` → `review` → `approved` → `deprecated` → `archived` |

### Category Taxonomy

| Category | Slug | Description |
|----------|------|-------------|
| Quality | `quality` | AI output quality boosters |
| Composition | `composition` | Camera framing, angles, lens effects |
| Lighting | `lighting` | Lighting types and atmosphere |
| Character | `character` | Character physical attributes |
| Clothing | `clothing` | Clothing and accessories |
| Styles | `styles` | Art and rendering styles |
| Negative | `negative` | Negative prompt keywords |
| Scene | `scene` | Scene and environment |
| Panel | `panel` | Panel-specific effects |

### Subcategory Highlights

**Quality** — `basic` · `advanced` · `anime`
> masterpiece, best quality, ultra-detailed, 8k resolution

**Character** — `hair` · `hairColors` · `eyes` · `eyeColors` · `expression` · `pose` · `anatomy` · `bodyType` · `skin` · `age`
> white long hair, blue eyes, fair skin, determined expression

**Clothing** — `tops` · `bottoms` · `outfits` · `accessories` · `mj_v5_materials` · `mj_v5_matprops`
> school uniform, white blouse, pleated skirt, red ribbon

**Styles** — `anime` · `art` · `realism` · `specialty` · `artist` · `mj_v5_colors` · `mj_v5_colors2` · `mj_v5_design` · `mj_v5_digital` · `mj_v5_dimension` · `mj_v5_intangibles` · `mj_v5_mediums` · `mj_v5_themes` · `mj_v5_artists`
> anime style, cel shading, manga comic style

**Negative** — `quality` · `anatomy` · `face` · `composition` · `style` · `text` · `commonDefects`
> low quality, worst quality, bad anatomy, extra limbs

**Lighting** — `natural` · `dramatic` · `mood` · `dynamic` · `special` · `mj_v5_lighting` · `mj_v5_sfx`
> golden hour, cinematic lighting, volumetric rays

**Composition** — `framing` · `angles` · `lens` · `rules` · `mj_v5_camera` · `mj_v5_geometry` · `mj_v5_perspective` · `mj_v5_structure`
> close-up, wide shot, eye level, Dutch angle

**Scene** — `relationship` · `interaction` · `weather` · `time` · `mj_v5_geo` · `mj_v5_nature` · `mj_v5_objects` · `mj_v5_space`
> school rooftop, cozy bedroom, battlefield, urban street

**Panel** — `panelLayout` · `comicEffects` · `animation` · `panelMood`
> speed lines, motion blur, impact frames, screen tone

### Lifecycle States

```
draft → review → approved → archived
              ↕           ↕
          (rejected)  (deprecated) ↗
```

- **draft**: Newly added, not yet validated
- **review**: Submitted for review, awaiting approval
- **approved**: Verified, ready for production use
- **archived**: No longer used, kept for reference
- **deprecated**: Being phased out, replaced by newer alternatives

---

## 💡 Prompt Examples

### Comic Panel Prompt

**Full panel positive prompt:**

```
masterpiece, best quality, ultra-detailed, girl 16 years old white long hair blue eyes fair skin, medium shot, character centered in frame, School Rooftop, golden hour, warm sunset glow, backlit rim light, long shadows, dialogue: "Hello!"
```

**Full panel negative prompt:**

```
low quality, worst quality, bad anatomy, extra limbs, poorly drawn face, mutation, cropped, watermark, text, signature
```

**Character consistency reference:**

```
girl 16 years old white long hair blue eyes fair skin, full body character reference sheet on white background, multiple views: front view, side profile view, back view, three-quarter view, multiple facial expressions: happy, sad, angry, surprised, neutral
```

**Character outfit description:**

```
wearing white blouse, navy blue pleated skirt, red ribbon, black loafers
```

**Character expression description:**

```
determined expression, focused blue eyes, slight frown, firm mouth
```

### Scene Description Words

**Outdoor scene:**

```
school rooftop at sunset, golden hour lighting, long shadows stretching across the ground, wind blowing through white hair, cherry blossom petals floating in the air, city skyline visible in the distance
```

**Indoor scene:**

```
cozy bedroom, warm lamp light, books on shelves, window with curtains, afternoon sunlight streaming through, personal photos on the wall, tidy room
```

**Combat scene:**

```
dramatic low angle shot, dynamic action pose, punch forward, motion blur, debris flying, intense determined expression, high contrast lighting, dramatic shadows, cinematic composition
```

### Template Example

Using the **character reference template**:

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

**Rendered output:**

```
girl 16 years old white long twin tails hair blue almond eyes fair skin, red ribbon, school uniform
```

---

## 📝 Template Syntax

Templates use a Mustache-like syntax with variable placeholders:

| Syntax | Description | Example |
|--------|-------------|---------|
| `{{var}}` | Simple substitution | `{{hair_color}}` → `blonde` |
| `{{#if var}}...{{/if}}` | Conditional render | `{{#if age}} {{age}} years old{{/if}}` |
| `{{#each arr}}...{{/each}}` | Array iteration | `{{#each features}}, {{this}}{{/each}}` |
| `{{join arr ', '}}` | Join helper | `{{join styles ' | '}}` |
| `{{truncate text 50}}` | Truncate to 50 chars | `{{truncate desc 50}}` |

---

## 📦 Versioning

The warehouse follows semantic versioning:

| Type | Meaning |
|------|---------|
| **Major (1.x.x)** | Schema change, breaking format changes |
| **Minor (x.1.x)** | New categories or fields, backwards compatible |
| **Patch (x.x.1)** | Bug fixes, data corrections, new keywords |

Each `_meta.json` tracks version, schema version, and changelog entries.

Current version: **v1.0.3** — 5,545 keywords across 9 categories.

---

## 🔌 API Integration

PWS is designed to work with a REST API. The h3-comic-builder server already provides:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/keywords` | GET | List keywords (paginated, filterable) |
| `/api/keywords/search` | GET | Full-text search |
| `/api/templates` | GET | List templates |
| `/api/templates/:id/render` | POST | Render template with data |
| `/api/snapshots` | GET/POST | List or create snapshots |

---

## 🌍 Multi-Language Support

Keywords and templates support multiple languages:

```json
{
  "term": "blonde hair",
  "term_zh": "金发",
  "term_ja": "ブロンドヘア",
  "labels": ["hair", "color", "blonde"],
  "labels_zh": ["头发", "颜色", "金色"],
  "labels_ja": ["髪", "色", "ブロンド"]
}
```

---

## 📊 Project Status

| Phase | Status | Details |
|-------|--------|---------|
| **Phase 1: Schema Definition** | ✅ Complete | 3 JSON schemas defined and validated |
| **Phase 2: Migration** | ✅ Complete | 4,429 keywords migrated from h3-comic-builder + MJ reference |
| **Phase 3: Tooling** | 🔄 In Progress | Browser UI for keyword management |
| **Phase 4: Sharing** | 📋 Planned | Remote sync, team collaboration, template marketplace |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** this repository
2. **Browse** existing keywords in `keywords/categories/`
3. **Add** new keywords following the schema in `schema/keyword.schema.json`
4. **Submit** a pull request

Guidelines:
- Keep `term` in English (canonical form)
- Add `labels` for searchability
- Set appropriate `score` and `priority`
- Follow the `{category}_{subcategory}_{slug}` id convention
- Run existing keywords through a generation test before setting `lifecycle: "approved"`

---

## 📄 License

MIT License — see [STANDARD_en.md](STANDARD_en.md) for full details.

---

## 📚 Resources

- **Full Specification**: [STANDARD_en.md](STANDARD_en.md)
- **Keyword Schema**: [schema/keyword.schema.json](schema/keyword.schema.json)
- **Template Schema**: [schema/template.schema.json](schema/template.schema.json)
- **Project Schema**: [schema/project.schema.json](schema/project.schema.json)
- **Metadata**: [keywords/_meta.json](keywords/_meta.json)
- **Current Stats**: 5,545 keywords · 9 categories · 24 templates

---

*Prompt Warehouse Standard v1.0 · Built for comic/manga prompt generation, applicable to any AI creative tool.*

*← [简体中文](README_zh.md)*
