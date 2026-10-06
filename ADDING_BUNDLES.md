# Adding Prompt Bundles

Prompt bundles (配方包/组合包) are curated combinations of keyword IDs, weights, and template references that form reusable prompt recipes. A single bundle can reference dozens of keywords with different weights and force-include flags, producing ready-to-use prompts for specific creative goals.

## Quick Start

### List Available Bundles

```bash
python3 tools/pws-bundles.py list
```

### Show a Bundle's Prompt

```bash
python3 tools/pws-bundles.py show photography.cinematic_portrait
```

### Generate a Customized Prompt

```bash
python3 tools/pws-bundles.py resolve photography.cinematic_portrait \
    --subject "a young woman" --setting "coastal cliff at sunset"
```

### View Detailed Bundle Info

```bash
python3 tools/pws-bundles.py info photography.cinematic_portrait
```

### Validate All Bundles

```bash
python3 tools/pws-bundles.py validate
```

## Bundle Structure

Each bundle is a standalone JSON file in the `bundles/` directory:

```jsonc
{
  "id": "photography.cinematic_portrait",
  "name": "Cinematic Portrait",
  "name_zh": "电影感人像",
  "version": "1.0.0",
  "category": "photography",
  "subcategories": ["portrait", "cinematic", "editorial"],
  "api_targets": ["SDXL", "Midjourney", "Flux"],

  // Reference existing keywords with weights and force flags
  "keywords": [
    {"id": "quality_basic_masterpiece", "weight": 0.95, "force_include": true},
    {"id": "composition_lens_85mm_portrait_lens", "weight": 0.9},
    {"id": "mj_mj_v5_lighting_cinematic_lighting", "weight": 0.95}
  ],

  // Optional: pre-built prompt text (used directly without resolution)
  "prompt_text": "masterpiece, best quality, 85mm portrait lens, ...",
  "prompt_text_zh": "杰作，最高质量，85mm人像镜头，...",

  // Optional: template references for video/image pipelines
  "templates": [
    {"template_id": "h3.video_prompts", "variant_id": "cinematic_reveal"}
  ],

  // Example usage
  "example": {
    "description": "Generate a cinematic editorial portrait.",
    "description_zh": "生成电影感人像摄影。",
    "input": {"subject": "...", "setting": "..."},
    "output": "masterpiece, best quality, ..., --v 6 --ar 2:3"
  },

  "tags": ["cinematic", "portrait", "editorial"],
  "lifecycle": "approved",
  "score": 0.92,
  "notes": "Combines quality boosters + 85mm lens + cinematic lighting.",
  "created_at": "2026-10-06T00:00:00+00:00",
  "updated_at": "2026-10-06T00:00:00+00:00"
}
```

## Key Concepts

### Keyword Weights

Each keyword in a bundle has a `weight` (0–1):

- **0.95+**: Force include — always appears in resolved prompt, even if context overrides
- **0.8–0.9**: High priority — appears early in the prompt
- **0.5–0.8**: Standard — included based on context
- **0.1–0.5**: Low priority — background detail, may be omitted in short prompts

### Force Include

`"force_include": true` ensures a keyword always appears in the output, regardless of context. Use for essential quality boosters and negative keywords.

### Pre-built Prompt Text

When `prompt_text` is provided, the bundle's resolve command uses it directly without keyword resolution. This is ideal for bundles that users want to use as-is.

### Template References

Bundles can reference templates from `templates/*.json` to produce structured prompts for specific APIs (e.g., Midjourney `--v 6 --ar 2:3` parameters).

## Creating a New Bundle

1. **Find relevant keyword IDs**: Search existing categories for keywords you want to combine:
   ```bash
   python3 tools/pws-audit.py
   ```

2. **Create the bundle file**: `bundles/{category}.{subcategory}.{slug}.json`

3. **Validate**:
   ```bash
   python3 tools/pws-bundles.py validate
   ```

4. **Test**:
   ```bash
   python3 tools/pws-bundles.py resolve your-bundle-id
   ```

5. **Review the example** in your bundle file to ensure the output prompt is useful.

## Bundle vs. Keyword vs. Template

| Concept | What it is | When to use |
|---------|-----------|-------------|
| **Keyword** | Single term (e.g. "masterpiece") | Add to your own prompts manually |
| **Template** | Prompt framework with variables | Specific API needs (SDXL, video, etc.) |
| **Bundle** | Pre-combined keywords + weights + prompt | Ready-to-use recipe for a creative goal |

A bundle is like a "preset" — it combines the right keywords at the right weights for a specific style or goal, saving you from memorizing which quality boosters go with which lighting keywords.
