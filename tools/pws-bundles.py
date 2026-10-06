#!/usr/bin/env python3
"""
pws-bundles — Prompt Warehouse Bundle Manager

List, resolve, and generate prompts from prompt bundles (recipe combos).

Usage:
  # List all available bundles
  python3 tools/pws-bundles.py list

  # List a specific bundle
  python3 tools/pws-bundles.py show photography.cinematic_portrait

  # Resolve a bundle to its raw prompt text
  python3 tools/pws-bundles.py resolve photography.cinematic_portrait

  # Generate a prompt with custom variables
  python3 tools/pws-bundles.py resolve photography.cinematic_portrait \
      --subject "a young woman" --setting "coastal cliff at sunset"

  # Show bundle details (all keywords with weights)
  python3 tools/pws-bundles.py info photography.cinematic_portrait

  # Validate all bundles against schema
  python3 tools/pws-bundles.py validate

"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

BUNDLES_DIR = "bundles"
META_PATH = "keywords/_meta.json"
INDEX_PATH = "data/pws_index.json"
SCHEMA_PATH = "schema/bundle.schema.json"


def safe_load_json(path: str) -> dict:
    """Load a JSON file with error handling."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to load {path}: {e}")
        sys.exit(1)


def load_all_keywords() -> dict:
    """Load all keywords into a dict keyed by ID."""
    keywords = {}
    for fp in glob.glob("keywords/categories/*.json"):
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    keywords[item.get("id", "")] = item
        except (json.JSONDecodeError, OSError):
            pass
    return keywords


def load_all_templates() -> dict:
    """Load all templates into a dict keyed by ID."""
    templates = {}
    for fp in glob.glob("templates/*.json"):
        if "_meta" in fp or "_legacy" in fp:
            continue
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
            templates[data.get("id", "")] = data
        except (json.JSONDecodeError, OSError):
            pass
    return templates


def load_bundle(bundle_id: str) -> dict:
    """Load a specific bundle by ID."""
    # Find the file: bundles/{id}.json
    fp = os.path.join(BUNDLES_DIR, f"{bundle_id}.json")
    if not os.path.exists(fp):
        print(f"❌ Bundle not found: {bundle_id}")
        print(f"  Expected file: {fp}")
        print("  Run 'python3 tools/pws-bundles.py list' to see available bundles.")
        sys.exit(1)
    return safe_load_json(fp)


def load_bundles() -> list:
    """Load all bundles from the bundles/ directory."""
    bundles = []
    for fp in sorted(glob.glob(os.path.join(BUNDLES_DIR, "*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
            data["_file"] = fp
            bundles.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️  Skipped {fp}: {e}")
    return bundles


def resolve_keyword_ids(bundle: dict, keywords: dict) -> str:
    """Resolve keyword IDs to their term text, sorted by weight."""
    parts = []
    forced = []
    for kw_ref in bundle.get("keywords", []):
        kw_id = kw_ref.get("id", "")
        weight = kw_ref.get("weight", 0.5)
        kw = keywords.get(kw_id, {})
        term = kw.get("term", kw_ref.get("fallback_term", kw_id))
        entry = (term, weight, kw_ref.get("force_include", False))
        if kw_ref.get("force_include", False):
            forced.append(entry)
        else:
            parts.append(entry)

    # Put forced keywords first, then sort rest by weight desc
    result = [p[0] for p in forced] + [p[0] for p in sorted(parts, key=lambda x: -x[1])]
    return ", ".join(result)


def resolve_templates(bundle: dict, templates: dict) -> str | None:
    """Resolve template references and return prompt text."""
    template_refs = bundle.get("templates", [])
    if not template_refs:
        return None

    for ref in template_refs:
        template_id = ref.get("template_id", "")
        variant_id = ref.get("variant_id", "")
        variables = ref.get("variables", {})

        tpl = templates.get(template_id, {})
        variants = tpl.get("variants", [])
        variant = None
        for v in variants:
            if v.get("id") == variant_id:
                variant = v
                break

        if variant:
            tpl_text = variant.get("template", "")
            # Substitute variables
            for var_name, var_value in variables.items():
                placeholder = "{{" + var_name + "}}"
                if placeholder in tpl_text:
                    tpl_text = tpl_text.replace(placeholder, var_value)
            return tpl_text

    return None


def generate_prompt(bundle: dict, keywords: dict, templates: dict,
                    extra_vars: dict | None = None) -> str:
    """Generate a complete prompt from a bundle."""
    extra_vars = extra_vars or {}

    # Use pre-built prompt_text if available
    if bundle.get("prompt_text"):
        base_prompt = bundle["prompt_text"]
    else:
        base_prompt = resolve_keyword_ids(bundle, keywords)

    # Resolve template if no pre-built prompt
    if not bundle.get("prompt_text"):
        tpl_text = resolve_templates(bundle, templates)
        if tpl_text:
            # Combine: keywords + template
            kw_text = resolve_keyword_ids(bundle, keywords)
            base_prompt = f"{kw_text}, {tpl_text}"

    # Apply example overrides if provided
    example = bundle.get("example", {})
    if example and isinstance(example, dict):
        for var_name, var_value in extra_vars.items():
            placeholder = "{{" + var_name + "}}"
            if placeholder in base_prompt:
                base_prompt = base_prompt.replace(placeholder, var_value)

    return base_prompt


def print_list(bundles: list):
    """Print a summary list of all bundles."""
    print(f"\n{'=' * 70}")
    print(f"  Prompt Bundles — {len(bundles)} bundle(s)")
    print(f"{'=' * 70}")

    for b in bundles:
        nid = b.get("id", "?")
        nm = b.get("name", "?")
        nm_zh = b.get("name_zh", "")
        kw_count = len(b.get("keywords", []))
        has_prompt = "✅" if b.get("prompt_text") else "❌"
        print(f"\n  [{has_prompt}] {nid}")
        print(f"        {nm} — {nm_zh}")
        print(f"        {kw_count} keywords · {b.get('category', '?')} · v{b.get('version', '?')}")
        if b.get("description"):
            desc = b["description"][:100]
            if len(b["description"]) > 100:
                desc += "..."
            print(f"        {desc}")
    print()


def print_info(bundle: dict, keywords: dict):
    """Print detailed info for a single bundle."""
    nid = bundle.get("id", "?")
    print(f"\n{'=' * 70}")
    print(f"  Bundle: {nid}")
    print(f"{'=' * 70}")
    print(f"  Name:     {bundle.get('name', '?')}")
    print(f"  名称:     {bundle.get('name_zh', '')}")
    print(f"  描述:     {bundle.get('description', 'N/A')}")
    print(f"  版本:     {bundle.get('version', '?')}")
    print(f"  分类:     {bundle.get('category', '?')}")
    if bundle.get("subcategories"):
        print(f"  子分类:   {', '.join(bundle['subcategories'])}")
    if bundle.get("api_targets"):
        print(f"  目标API:   {', '.join(bundle['api_targets'])}")

    # Keywords
    print(f"\n  {'=' * 70}")
    print(f"  Keywords ({len(bundle.get('keywords', []))}):")
    print(f"  {'-' * 70}")
    for kw_ref in bundle.get("keywords", []):
        kw_id = kw_ref.get("id", "?")
        kw = keywords.get(kw_id, {})
        term = kw.get("term", kw_ref.get("fallback_term", "?"))
        weight = kw_ref.get("weight", 0.5)
        force = "⚡" if kw_ref.get("force_include") else "  "
        print(f"    {force} [{weight:.2f}] {kw_id}")
        if kw.get("term_zh"):
            print(f"             {term} -> {kw['term_zh']}")
        else:
            print(f"             {term}")

    # Prompt text
    print(f"\n  {'=' * 70}")
    prompt = bundle.get("prompt_text", "")
    if prompt:
        print(f"  预建提示词: {prompt}")
    else:
        print("  无预建提示词 (需要通过 resolve 命令生成)")

    # Example
    example = bundle.get("example")
    if example and isinstance(example, dict):
        print(f"\n  {'=' * 70}")
        print("  示例:")
        if example.get("description_zh"):
            print(f"    {example['description_zh']}")
        if example.get("output"):
            print(f"    输出: {example['output'][:120]}...")
        if example.get("negative"):
            print(f"    负面: {example['negative']}")

    print(f"\n{'=' * 70}\n")


def do_validate(bundles: list, keywords: dict, templates: dict) -> int:
    """Validate all bundles against the schema."""
    errors = 0
    print(f"\n{'=' * 70}")
    print(f"  Validating {len(bundles)} bundle(s)...")
    print(f"{'=' * 70}")

    for b in bundles:
        bid = b.get("id", "unknown")
        print(f"\n  Checking {bid}...", end="")

        # Check required fields
        required = ["id", "name", "name_zh", "keywords", "version"]
        missing = [f for f in required if f not in b]
        if missing:
            print(f" ❌ Missing: {', '.join(missing)}")
            errors += 1
            continue

        # Check keywords reference valid keyword IDs
        valid_ids = set(keywords.keys())
        for kw_ref in b.get("keywords", []):
            kw_id = kw_ref.get("id", "")
            if kw_id not in valid_ids:
                print(f" ❌ Unknown keyword ID: {kw_id}")
                errors += 1
                break
        else:
            print(" ✅")

    # Check templates
    valid_tids = set(templates.keys())
    for b in bundles:
        bid = b.get("id", "unknown")
        for tref in b.get("templates", []):
            tid = tref.get("template_id", "")
            if tid and tid not in valid_tids:
                print(f"  ⚠️  {bid}: Unknown template ID {tid}")

    print(f"\n  ✅ Validation complete: {len(bundles) - errors} ok, {errors} errors")
    print(f"{'=' * 70}")
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="PWS Bundle Manager — manage prompt recipe bundles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all available bundles")

    # show
    show_parser = subparsers.add_parser("show", help="Show bundle prompt text")
    show_parser.add_argument("bundle_id", help="Bundle ID (e.g. photography.cinematic_portrait)")
    show_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # resolve
    resolve_parser = subparsers.add_parser("resolve", help="Generate prompt text from bundle")
    resolve_parser.add_argument("bundle_id", help="Bundle ID (e.g. photography.cinematic_portrait)")
    resolve_parser.add_argument("--subject", help="Override subject variable")
    resolve_parser.add_argument("--setting", help="Override setting variable")
    resolve_parser.add_argument("--emotion", help="Override emotion variable")
    resolve_parser.add_argument("--scene-type", dest="scene_type", help="Override scene_type variable")
    resolve_parser.add_argument("--atmosphere", help="Override atmosphere variable")
    resolve_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    info_parser = subparsers.add_parser("info", help="Show detailed bundle info")
    info_parser.add_argument("bundle_id", help="Bundle ID (e.g. photography.cinematic_portrait)")

    # validate
    subparsers.add_parser("validate", help="Validate all bundles")

    args = parser.parse_args()

    # Load shared data
    keywords = load_all_keywords()
    templates = load_all_templates()

    if args.command == "list":
        bundles = load_bundles()
        print_list(bundles)

    elif args.command == "show":
        bundle = load_bundle(args.bundle_id)
        if args.json:
            print(json.dumps(bundle, ensure_ascii=False, indent=2))
        else:
            print(f"  Prompt: {bundle.get('prompt_text', '(no pre-built prompt)')}")
            zh = bundle.get("prompt_text_zh", "")
            if zh:
                print(f"  提示词: {zh}")

    elif args.command == "resolve":
        bundle = load_bundle(args.bundle_id)
        extra_vars = {
            "subject": args.subject,
            "setting": args.setting,
            "emotion": args.emotion,
            "scene_type": args.scene_type,
            "atmosphere": args.atmosphere,
        }
        # Clean None values
        extra_vars = {k: v for k, v in extra_vars.items() if v}

        if args.json:
            result = {
                "bundle_id": args.bundle_id,
                "name": bundle.get("name"),
                "name_zh": bundle.get("name_zh"),
                "prompt": generate_prompt(bundle, keywords, templates, extra_vars),
                "negative": bundle.get("example", {}).get("negative", ""),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            prompt = generate_prompt(bundle, keywords, templates, extra_vars)
            print(f"\n{'=' * 70}")
            print(f"  Bundle: {args.bundle_id} ({bundle.get('name_zh', bundle.get('name', ''))})")
            print(f"{'=' * 70}")
            print(f"\n  Prompt:\n  {prompt}")

            neg = bundle.get("example", {}).get("negative", "")
            if neg:
                print(f"\n  Negative prompt:\n  {neg}")
            print()

    elif args.command == "info":
        bundle = load_bundle(args.bundle_id)
        print_info(bundle, keywords)

    elif args.command == "validate":
        bundles = load_bundles()
        errs = do_validate(bundles, keywords, templates)
        sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
