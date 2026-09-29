# Prompt Warehouse Standard Specification

> **pws v1.0** — Prompt Warehouse Standard
>
> A unified, language-agnostic standard for organizing, versioning, and sharing
> AI generation prompts across projects. Designed for comic/manga prompt generation
> but applicable to any AI creative tool (image, video, text, music).
>
> **Repository**: https://github.com/zz3656/prompt-warehouse
> **License**: MIT

---

## 1. Philosophy

### 1.1 Why This Standard?

Current prompt management suffers from:
- **Silos**: Each project has its own keyword files, templates, and data models
- **No versioning**: Hard to track which version of a prompt produced what result
- **No sharing**: Cannot easily reuse good prompts across projects
- **No structure**: Prompts are strings in JS objects with no machine-readable schema
- **No lifecycle**: No concept of draft/review/approved/archived

This standard solves these problems by providing:
1. A **data schema** for all prompt-related entities
2. A **file format** (JSON) that's human-readable and machine-parseable
3. A **versioning system** for tracking changes
4. A **tagging taxonomy** for cross-project discovery
5. A **lifecycle management** system (draft → review → approved → archived, including deprecated)

### 1.2 Scope

| Entity | Description |
|--------|-------------|
| `tag` | Building block of a prompt (single keyword or phrase) |
| `tag_category` | Grouping of tags (e.g. "hair color", "lighting type") |
| `keyword` | Structured tag with metadata (category, subcategory, labels, scores) |
| `template` | Reusable prompt template with variable placeholders |
| `prompt` | Concrete prompt instance (template rendered with values) |
| `project` | Application-level config referencing keywords and templates |
| `snapshot` | Exported prompt output with usage context and results |

---

## 2. Directory Structure

```
prompt-warehouse/
├── schema/                     # JSON Schema definitions (machine-readable)
│   ├── keyword.schema.json
│   ├── template.schema.json
│   └── project.schema.json
├── keywords/                   # Keyword dictionary (the "database")
│   ├── _meta.json              # Global metadata + version
│   └── categories/             # One file per top-level category
│       ├── quality.json
│       ├── composition.json
│       ├── lighting.json
│       ├── character.json
│       ├── clothing.json
│       ├── styles.json
│       ├── negative.json
│       ├── scene.json
│       └── panel.json
├── templates/                  # Prompt templates
│   ├── _meta.json
│   ├── character_sheet.json
│   ├── panel_prompt.json
│   └── reference_description.json
├── projects/                   # Per-project configs
│   └── h3-comic-builder.json
├── snapshots/                  # Export snapshots
│   └── YYYY/MM/
└── README_en.md                # This file
```

---

## 3. Data Models

### 3.1 Keyword Model

Every keyword (tag) is a structured object:

```json
{
  "id": "qc_blonde_hair",
  "term": "blonde hair",
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
  "notes": "Works well with SDXL anime models. Avoid with photorealistic.",
  "variations": [
    {"term": "platinum blonde hair", "context": "high-value characters"},
    {"term": "strawberry blonde hair", "context": "warm lighting"}
  ]
}
```

#### Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier. Format: `{category}_{subcategory}_{slug}` |
| `term` | string | ✅ | The canonical prompt term in English |
| `aliases` | string[] | | Alternative terms (non-English, colloquial) |
| `category` | string | ✅ | Top-level category (see taxonomy) |
| `subcategory` | string | ✅ | Sub-category within category |
| `labels` | string[] | | Flat search labels (auto-indexed) |
| `score` | number | | Quality score 0-1 (default: 0.5) |
| `priority` | enum | | `high` / `medium` / `low` / `experimental` |
| `lifecycle` | enum | | `draft` / `review` / `approved` / `deprecated` / `archived` |
| `tags` | string[] | | User-defined tags for cross-cutting concerns |
| `created_at` | iso-date | | ISO 8601 timestamp |
| `updated_at` | iso-date | | ISO 8601 timestamp |
| `source` | string | | Where this keyword came from (source attribution) |
| `usage_count` | number | | How many times this has been used (default: 0) |
| `success_rate` | number | | Ratio of successful generations (0-1, default: null) |
| `notes` | string | | Human-readable notes |
| `variations` | array | | Context-specific alternative terms |

#### Lifecycle States

```
draft → review → approved → archived
              ↕           ↕
          (rejected)  (deprecated) ↗
          deprecated ↗
```

- **draft**: Newly added, not yet validated
- **review**: Submitted for review, awaiting approval
- **approved**: Verified, ready for production use
- **archived**: No longer relevant, kept for historical reference
- **deprecated**: Being phased out, replaced by newer alternatives

---

### 3.2 Category Taxonomy

```
quality           — AI output quality boosters
  ├── basic       — Standard quality tags
  ├── advanced    — High-end quality tags
  └── anime       — Anime-specific quality tags

composition       — Camera framing, angles, lens effects
  ├── framing     — Shot sizes (close-up, wide, etc.)
  ├── angles      — Camera angles
  ├── lens        — Lens types and effects
  └── rules       — Composition rules

lighting          — Lighting types and atmosphere
  ├── natural     — Natural light (sunlight, golden hour)
  ├── dramatic    — Dramatic/studio lighting
  ├── mood        — Mood lighting (cool, neon, etc.)
  ├── dynamic     — Dynamic atmospheric effects
  └── special     — Special effects (glow, particles)

character         — Character physical attributes
  ├── hair        — Hair styles and descriptions
  ├── hairColors  — Hair color variants
  ├── eyes        — Eye descriptions
  ├── eyeColors   — Eye color variants
  ├── expression  — Facial expressions
  ├── pose        — Body poses
  ├── anatomy     — Anatomy descriptors
  ├── bodyType    — Body types
  └── skin        — Skin tones

clothing          — Clothing and accessories
  ├── tops        — Upper body clothing
  ├── bottoms     — Lower body clothing
  ├── outfits     — Complete outfits
  └── accessories — Accessories and items

styles            — Art and rendering styles
  ├── anime       — Anime/manga style tags
  ├── art         — General art style tags
  ├── realism     — Photorealistic tags
  ├── specialty   — Specialty/niche styles
  └── artist      — Artist style references

negative          — Negative prompt keywords
  ├── quality     — Quality negatives
  ├── anatomy     — Anatomy failures
  ├── face        — Face failures
  ├── composition — Composition failures
  ├── style       — Style mismatches
  ├── text        — Text-related negatives
  └── defects     — Common generation defects

scene             — Scene and environment
  ├── relationship — Character relationships
  ├── interaction — Character interactions
  ├── weather     — Weather conditions
  └── time        — Time of day

panel             — Panel-specific effects
  ├── layout      — Panel layout types
  ├── effects     — Comic/manga visual effects
  ├── animation   — Animation-specific terms
  └── mood        — Panel emotional tone
```

---

### 3.3 Template Model

Templates use a simple Mustache-like syntax with `<variable>` placeholders (CLI-aligned):

```json
{
  "id": "character.reference_description",
  "name": "Character Reference Description",
  "description": "Compact character description for consistency across panels",
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
      "description": "Standard reference description",
      "template": "{{gender}}{{#if age}} {{age}} years old{{/if}}{{#if hair_color}} {{hair_color}}{{#if hair_style}} {{hair_style}}{{/if}} hair{{/if}}{{#if eye_color}} {{eye_color}} eyes{{/if}}{{#if skin_tone}} {{skin_tone}} skin{{/if}}{{#each distinctive_features}}, {{this}}{{/each}}"
    },
    {
      "id": "minimal",
      "description": "Minimal version for token-limited models",
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
  "notes": "Primary consistency mechanism. Must appear at start of every panel prompt for the same character."
}
```

---

### 3.4 Project Config Model

```json
{
  "id": "h3-comic-builder",
  "name": "H3 Comic Builder",
  "version": "1.0.0",
  "description": "AI comic/manga prompt generation tool",
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

### 3.5 Snapshot Model

```json
{
  "id": "snap_20250620_143000_001",
  "project": "h3-comic-builder",
  "timestamp": "2025-06-20T14:30:00Z",
  "type": "export",
  "title": "Chapter 1, Panels 1-5",
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

## 4. Migration: JSON → PWS Schema

### 4.1 Current h3-comic-builder Keyword Files

```
modules/
├── prompt_keywords_core.js      →  quality, composition, lighting
├── prompt_keywords_character.js →  character, clothing
└── prompt_keywords_scenes.js    →  styles, mood, scene, panel, negative
```

### 4.2 Migration Mapping

| Current Category | File | PWS Category File |
|-----------------|------|-------------------|
| QUALITY | core.js | `keywords/categories/quality.json` |
| COMPOSITION | core.js | `keywords/categories/composition.json` |
| LIGHTING | core.js | `keywords/categories/lighting.json` |
| CHARACTER.* | character.js | `keywords/categories/character.json` |
| CLOTHING.* | character.js | `keywords/categories/clothing.json` |
| STYLES.* | scenes.js | `keywords/categories/styles.json` |
| NEGATIVE.* | scenes.js | `keywords/categories/negative.json` |
| SCENE.* | scenes.js | `keywords/categories/scene.json` |
| PANEL_SPECIFIC.* | scenes.js | `keywords/categories/panel.json` |

### 4.3 Migration Script

A migration script (to be implemented) will:

1. Parse each `prompt_keywords_*.js` file using regex
2. Convert flat arrays to structured keyword objects
3. Apply default metadata (score, lifecycle, tags)
4. Generate proper IDs following the `{category}_{subcategory}_{slug}` convention
5. Output JSON files in the PWS directory structure
6. Preserve backwards compatibility with existing `.js` files

---

## 5. Template Syntax

### 5.1 Variables

| Syntax | Description |
|--------|-------------|
| `{{var}}` | Simple variable substitution |
| `{{obj.field}}` | Nested property access |
| `{{array.0}}` | Array index access |

### 5.2 Conditionals

| Syntax | Description |
|--------|-------------|
| `{{#if var}}content{{/if}}` | Render if var is truthy |
| `{{#unless var}}content{{/unless}}` | Render if var is falsy |
| `{{#equals a 'b'}}content{{/equals}}` | Render if a equals b |
| `{{#notEquals a 'b'}}content{{/notEquals}}` | Render if a doesn't equal b |
| `{{#between a 1 10}}content{{/between}}` | Render if a is between 1 and 10 |

### 5.3 Iteration

| Syntax | Description |
|--------|-------------|
| `{{#each array}}item{{/each}}` | Iterate array |
| `{{#each obj}}key=value{{/each}}` | Iterate object |
| `{{@index}}` | Current index in iteration |
| `{{@key}}` | Current key in object iteration |
| `{{@first}}` | Boolean: is this the first item? |
| `{{@last}}` | Boolean: is this the last item? |

### 5.4 Helpers

| Helper | Usage | Description |
|--------|-------|-------------|
| `join` | `{{join array ', '}}` | Join array with separator |
| `length` | `{{length array}}` | Get array length |
| `escape` | `{{escape text}}` | HTML-escape text |
| `default` | `{{default var 'fallback'}}` | Fallback value |
| `upper` | `{{upper text}}` | Uppercase |
| `lower` | `{{lower text}}` | Lowercase |
| `trim` | `{{trim text}}` | Trim whitespace |
| `truncate` | `{{truncate text 50}}` | Truncate to N chars |

### 5.5 Iteration Helpers (inside `each`)

| Helper | Usage | Description |
|--------|-------|-------------|
| `@@index` | Inside `each` | Current 0-based index |
| `@@first` | Inside `each` | Is first item |
| `@@last` | Inside `each` | Is last item |
| `@@key` | Object each | Current key |

---

## 6. Versioning

### 6.1 File Version

Every `_meta.json` file contains:

```json
{
  "version": "1.0.0",
  "schema_version": "pws-1.0",
  "updated_at": "2025-06-20T14:30:00Z",
  "updated_by": "migration-script",
  "commit": "abc123"
}
```

### 6.2 Increment Rules

- **Major (1.x.x)**: Schema change, breaking format changes
- **Minor (x.1.x)**: New categories or fields, backwards compatible
- **Patch (x.x.1)**: Bug fixes, data corrections, new keywords

### 6.3 Git Integration

Each keyword/template change should include:
- A commit message following conventional commits format
- A `CHANGELOG.md` entry in the warehouse root
- Optional: a `review.md` file in the category directory for pending changes

---

## 7. API Integration (REST)

The PWS standard is designed to work with a REST API like the h3-comic-builder server:

### Keywords API
```
GET    /api/keywords           List keywords (paginated, filterable)
GET    /api/keywords/:id       Get keyword detail
POST   /api/keywords           Create keyword
PUT    /api/keywords/:id       Update keyword
DELETE /api/keywords/:id       Delete keyword
GET    /api/keywords/search    Full-text search
GET    /api/keywords/stats     Usage analytics
POST   /api/keywords/import    Bulk import (JSON/CSV)
GET    /api/keywords/export    Full export
```

### Templates API
```
GET    /api/templates              List templates
GET    /api/templates/:id          Get template
POST   /api/templates              Create template
PUT    /api/templates/:id          Update template
DELETE /api/templates/:id          Delete template
POST   /api/templates/:id/render   Render template with data
```

### Snapshots API
```
GET    /api/snapshots              List snapshots
GET    /api/snapshots/:id          Get snapshot
POST   /api/snapshots              Import/create snapshot
DELETE /api/snapshots/:id          Delete snapshot
```

---

## 8. Multi-Language Support

### 8.1 Keyword Labels

Keywords support multiple language labels:

```json
{
  "id": "qc_graceful_lighting",
  "term": "beautiful lighting",
  "labels": ["lighting", "glow", "illumination"],
  "labels_zh": ["灯光", "光影", "光线", "美丽"],
  "labels_ja": ["照明", "光", "影", "美しい"],
  "term_zh": "美丽的光线",
  "term_ja": "美しい照明"
}
```

### 8.2 Template Languages

Templates can have language-specific variants:

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

## 9. Example: Converting Current Data

### Before (prompt_keywords_core.js):
```javascript
var QUALITY = {
  basic: [
    'masterpiece', 'best quality', 'high quality', 'high resolution'
  ]
};
```

### After (keywords/categories/quality.json):
```json
[
  {
    "id": "qc_basic_masterpiece",
    "term": "masterpiece",
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

## 10. Adoption Guide

### Phase 1: Schema Definition (Current)
- [x] Define data models (keyword, template, project, snapshot)
- [x] Create JSON Schema files for validation
- [x] Document the standard

### Phase 2: Migration
- [ ] Create migration script from `.js` files to JSON
- [ ] Run migration on h3-comic-builder data
- [ ] Validate all ~350 keywords are preserved
- [ ] Update admin backend to serve JSON instead of parsing `.js` files

### Phase 3: Tooling
- [ ] CLI tool for managing the warehouse (`pws`)
- [ ] Web UI for keyword management (extends current admin)
- [ ] Search and analytics dashboard
- [ ] Import/export tools (CSV, Excel, JSON)

### Phase 4: Sharing
- [ ] Remote repository sync
- [ ] Team collaboration features
- [ ] Prompt rating and feedback
- [ ] Template marketplace

---

## Appendix A: Category Reference

| Category | Slug | Default Score | Lifecycle |
|----------|------|---------------|-----------|
| Quality | `quality` | 0.85 | approved |
| Composition | `composition` | 0.75 | approved |
| Lighting | `lighting` | 0.80 | approved |
| Character | `character` | 0.70 | approved |
| Clothing | `clothing` | 0.65 | approved |
| Styles | `styles` | 0.75 | approved |
| Negative | `negative` | 0.90 | approved |
| Scene | `scene` | 0.60 | approved |
| Panel | `panel` | 0.65 | approved |

## Appendix B: Score Interpretation

| Score Range | Meaning |
|-------------|---------|
| 0.90 - 1.00 | Proven, industry-standard, almost always effective |
| 0.70 - 0.89 | Reliable, commonly used, good results |
| 0.50 - 0.69 | Situationally useful, model-dependent |
| 0.30 - 0.49 | Experimental, niche, low confidence |
| 0.00 - 0.29 | Unverified, needs testing |

## Appendix C: Future Extensions

- **Prompt chaining**: Connect multiple templates into pipelines
- **A/B testing**: Track which keywords perform better
- **Model-specific variants**: Different versions for SDXL vs MJ vs DALL-E
- **Prompt diff**: Visual comparison between prompt versions
- **Prompt chat**: Natural language query: "Show me all lighting keywords for night scenes"
- **Prompt plagiarism check**: Detect if two prompts are too similar

---

*← [简体中文](STANDARD_zh.md)*
