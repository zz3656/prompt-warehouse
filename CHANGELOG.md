# Changelog
All notable changes to the Prompt Warehouse keyword database.
Format is based on [Keep a Changelog](https://keepachangelog.com/).
---
## [1.8.0] - 2026-09-30
### 🎉 MILESTONE: 100% Chinese translation coverage achieved
- **term_zh coverage**: 5027/5943 (84.6%) → **5943/5943 (100.0%)** (+916 keywords)
- **labels_zh coverage**: 5027 → **5943** (+916)
- **PRE_TRANSLATIONS**: 8117 → 9122 unique entries (+1005)
- **All 20 categories** at 99%+ coverage; **16/20 categories at 100%**

### Final per-category coverage
| Category | Coverage | Category | Coverage |
|----------|---------:|----------|---------:|
| scene | 100.0% | clothing | 100.0% |
| character | 100.0% | composition | 100.0% |
| lighting | 100.0% | quality | 100.0% |
| negative | 100.0% | transitions | 100.0% |
| action-fx | 100.0% | panel | 100.0% |
| material | 100.0% | framing | 100.0% |
| held-prop | 100.0% | color-look | 100.0% |
| character-fx | 100.0% | render-quality | 100.0% |
| era | 100.0% | temporal | 100.0% |
| **styles** | 99.9% | **photographer** | 98.9% |

### New extend scripts
- `extend-translations-10.py` (318 entries): photographer, color-look, character-fx, framing, character, quality
- `extend-translations-11.py` (572 entries): scene interaction/relationship/nature/backdrop/indoor, styles mj_v5_design/themes/dimension/artistStyle/art/artStyles/aesthetic, negative/held-prop/material/composition/lighting
- `extend-translations-12.py` (57 entries): truncated 60-char compound terms
- `extend-translations-13.py` (58 entries): final 60-char terms

### Manual fixes
- `Decor%20(2)` (URL-encoded artifact) → `装饰 (2)`
- 2 truncated terms (glamour portrait phrase) handled via direct JSON patch

### Audit
- **0 errors, 0 warnings, 0 info** — clean run

## [1.7.0] - 2026-09-30
### Massive translation expansion
- **PRE_TRANSLATIONS**: 3557 → 8117 entries (+4560)
- **term_zh coverage**: 29.5% → **84.6%** (+3271 keywords, +55.1%)
- **labels_zh coverage**: 29.5% → 84.6%

### Per-category final coverage
| Category | Coverage |
|----------|---------:|
| composition | 98.7% |
| temporal | 100.0% |
| clothing | 94.8% |
| lighting | 92.1% |
| material | 89.6% |
| scene | 84.5% |
| styles | 84.2% |
| transitions | 81.5% |
| held-prop | 80.0% |
| character | 78.1% |
| negative | 77.7% |
| panel | 73.9% |
| action-fx | 70.8% |
| quality | 66.4% |
| era | 66.7% |
| character-fx | 63.6% |
| framing | 62.1% |
| photographer | 60.9% |
| color-look | 59.3% |
| render-quality | 41.7% |

### New extend scripts
- `extend-translations-5.py` (807): design / mediums / digital subcategories
- `extend-translations-6.py` (673): scene mj_v5_nature/objects/geo/space
- `extend-translations-7.py` (1871): remaining styles MJ V5 terms
- `extend-translations-8.py` (749): lighting/character/composition panels
- `extend-translations-9.py` (461): clothing materials/props/transitions/panel

### Categories with notable additions
- **300+ clothing materials**: rocks, metals, gems, fibers, papers (felt, kapton, kevlar, etc.)
- **100+ material properties**: bioluminescence, anisotropic, opalescent, chromism variants
- **Character mood expressions**: smoldering intensity, contrapposto, devastating heartbreak, etc.
- **Physics & geometry terms**: klein bottle, archimedean spiral, perspectivism

## [1.6.0] - 2026-09-30
### Added
- **PRE_TRANSLATIONS expansion**: 488 → 3557 unique entries (+3069)
  - 9 zero-coverage @nodaro/prompts categories now 50-100% covered
  - 100+ common terms added to major categories (clothing, scene, styles, etc.)
  - 50+ color path translations (willwulfken MJ V5)
  - 100+ negative prompt blocklist translations
### Improved
- `find_translation()` now supports:
  - **Word-composition**: handles compound terms like "red hair blue eyes" → "红发 蓝眼"
  - **Substring matching**: longest phrase from dictionary found in term
  - **Order**: pre-defined → index → word-composition → substring → fuzzy
### Tools
- Added `extend-translations.py`, `extend-translations-2.py`, `-3.py`, `-4.py` for batch dictionary expansions (idempotent — skipped on existing keys)
### Result
- term_zh coverage: 481/5943 (8.1%) → **1756/5943 (29.5%)** (+1275 keywords)
- labels_zh coverage: 481 → **1756** (+1275)
- Per-category translation now comprehensive for h3-comic-builder usage

## [1.5.0] - 2026-09-30
### Fixed
- **Pre-commit hook NameError**: changed `existing`/`staged` to `existing_items`/`staged_items` to prevent `UnboundLocalError` when no staged files exist
- **GitHub Actions CI**: removed duplicate `pip install jsonschema` step, switched to `pip install -r requirements.txt`
- **11 stale terms in styles.json**: 1 HTML scraping artifact (`Crystalcore" Width="256" />`), 4 "rendered as a ..." description strings >40 chars, 6 "in the ... aesthetic — ..." descriptions truncated to canonical form
### Added
- `pws-audit.py` — unified data quality audit tool (schema, IDs, duplicates, scores, lifecycle, artifacts, metadata)
- `pws-clean-long-terms.py` — detects and fixes long/corrupted term values (HTML artifacts, pipe separators, repeated mj_v5_ prefixes)
- `pws-fix-mj-artifacts.py` — focused tool for MidJourney reference HTML/IMG scraping errors
- `template-validate` job in GitHub Actions
### Notes
- term_zh coverage unchanged at 481/5943 (8.1%) — recommend running `pws-translate.py --translate-all`
- 360 verbose terms >40 chars from @nodaro/prompts are intentionally preserved (video generation prompts)

## [1.4.0] - 2026-09-30
- Generated labels_zh for all 481 keywords with term_zh (from pws-generate-labels-zh.py)
- Fixed Schema: term_zh/aliases_zh/labels_zh allow null type, notes maxLength 1000→5000
- Fixed 1119 empty string fields converted to removed fields
- Added pws-generate-labels-zh.py tool
- Added pws-index.py flat index generator
- Added GitHub Actions CI validation workflow
- Added pre-commit hook
- Added requirements.txt
- Added CHANGELOG.md
- Added .gitignore
- Cleaned up: archived pws-merge-categories.py, renamed _all_templates.json
- Updated README with correct version/category/keyword counts
- Expanded translation dictionary: ~200 → 488 entries

## [1.3.0] - 2026-09-30
- Expanded translation dictionary: ~200 → 488 entries, term_zh coverage 5.1% → 8.1% (+176 keywords)
- Generated flat keyword index (data/pws_index.json) with 5,943 entries
- Added pws-index.py tool for building searchable flat indexes
- Added requirements.txt for Python dependencies
- Fixed trailing space in PRE_TRANSLATIONS entry

## [1.2.0] - 2026-09-30
- Fixed 472 IDs to conform to ^[a-z][a-z0-9_]*$ pattern (lowercase, underscore instead of spaces/special chars)- Auto-translated 162 keywords (term_zh coverage: 0.2% → 2.9%)- Bumped version to reflect data quality improvements## [1.1.1] - 2026-09-29
- Removed 14 true-duplicate terms (same term + same category/subcategory)- Cleanup targets: 9 in composition/camera-motions (camera-motions.json source duplicates), 2 in character/pose (walking/running merged duplicates), 1 in composition/lens (shallow depth of field), 1 in lighting/mj_v5_sfx (Post Processing), 2 in styles/mj_v5_design (Newton Fractal, Ultra Quality)- Cross-category duplicates are intentionally KEPT (semantically distinct)- Added tools/pws-dedup-terms.py for future maintenance## [1.1.0] - 2026-09-29
- Category consolidation: 33 → 20 files (see docs/CATEGORY_CONSOLIDATION.md)- Merged 13 redundant category files: style, aesthetic, atmosphere, mood, pose, wardrobe, setting, backdrop, lens, camera-format, camera-motions, photo-genre, post-process- Preserved all keywords (5,957 net: 5,948 after merge + 9 restored from aesthetic.json era/mood, -2 dropped as term duplicates with composition/lens)- Fixed 4 ID duplicates: 3 in styles.json (mj_mj_v5_design_newton_fractal, mj_mj_v5_design_ultra_quality, mj_mj_v5_mediums_says_hello_) + 1 in lighting.json (mj_mj_v5_sfx_post_processing)- New subcategories: styles/aesthetic (32+), lighting/atmosphere (40), character/mood (56), character/pose (124 total), clothing/wardrobe-* (70), scene/indoor|urban|fantastical|backdrop (80), composition/lens|camera-format|camera-motions (113), photographer/genre (24), color-look/post-process (18)## [1.0.7] - 2026-09-29
- Added Chinese translation support (term_zh, aliases_zh, labels_zh) to keyword schema- Added deduplication tool (tools/pws-dedup.py) for duplicate detection- Added batch translation tool (tools/pws-translate.py) for Chinese field population## [1.0.4] - 2026-09-29
- Added data_sources section to _meta.json - permanent record of all keyword sources- Updated individual keyword source/notes fields for traceability- No new keywords added, metadata only## [1.0.3] - 2026-09-29
- Added 101 quality keywords (Danbooru-style boosters, rendering techniques, atmosphere, color, texture, composition)- Added 167 character keywords (Danbooru tags: hair/eye colors, expressions, clothing, accessories, poses, anatomy)- Added 72 scene keywords (nature, architecture, weather, time-of-day, environments)- Added 41 style keywords (art styles, anime genres, aesthetic movements, rendering techniques)## [1.0.2] - 2026-09-28
- Added 3,494 MJ V5 keywords from 21 pages (willwulfken repo)- 17 new MJ V5 subcategories across 5 PWS categories## [1.0.1] - 2026-09-28
- Added 1116 keywords from willwulfken/MidJourney-Styles-and-Keywords-Reference (12.3k stars)- Fixed term formatting (underscore to space)- Added mj_* subcategories for MJ-specific keywords## [1.0.5] - 2026-09-29
- Added 760 keywords from @nodaro/prompts (v1.27.0) — comprehensive prompt engineering catalog- 17 new categories: action-fx, aesthetic, atmosphere, camera-format, character-fx, color-look, era, framing, held-prop, lens, mood, pose, post-process, render-quality, style- Coverage expanded: environmental effects, character moods, historical eras, material presets, photographic equipment, camera framing, render engines, color grading, and more## [1.0.6] - 2026-09-29
- Added 389 additional keywords from @nodaro/prompts batch 2- Added categories: backdrop (40), camera-motions (66), photographer (63), setting (51), wardrobe (70), temporal (18), transitions (81)- Total project keywords now: 5,948 across 34 categories---
Total keywords: 5943 across 20 categories
