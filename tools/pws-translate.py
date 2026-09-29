#!/usr/bin/env python3
"""
pws-translate — Prompt Warehouse 批量翻译工具

为关键词/模板的 term_zh, aliases_zh, labels_zh 字段补充中文翻译。

使用方法:
  1. 全自动模式（推荐）: 读取现有数据，生成翻译 JSON 映射，写入回文件
     python3 tools/pws-translate.py --translate-all --dry-run
     python3 tools/pws-translate.py --translate-all

  2. 指定文件模式:
     python3 tools/pws-translate.py --file keywords/categories/quality.json --dry-run
     python3 tools/pws-translate.py --file keywords/categories/quality.json

  3. 手动输入翻译模式（交互式）:
     python3 tools/pws-translate.py --interactive

  4. 仅生成翻译草稿（不写入，供人工审查）:
     python3 tools/pws-translate.py --generate-draft output/draft_translations.json

翻译数据写入 JSONL 格式的 _translations.jsonl 索引，便于后续人工审核和修改。
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher

# ---------- configuration ----------

TRANSLATIONS_INDEX = "_translations.jsonl"

# Pre-defined translation mappings for commonly used terms
# These serve as a baseline; the script can be extended with more mappings
PRE_TRANSLATIONS = {
    # quality/basic
    "masterpiece": "杰作",
    "best quality": "最高质量",
    "high quality": "高质量",
    "high resolution": "高分辨率",
    "ultra-detailed": "超精细",
    "ultra-realistic": "超写实",
    "award-winning": "获奖作品",
    "perfect composition": "完美构图",
    "photorealistic": "照片级写实",
    "8k": "8K",

    # quality/advanced
    "cinematic": "电影感",
    "volumetric lighting": "体积光",
    "ray tracing": "光线追踪",
    "global illumination": "全局光照",
    "hdr": "HDR",
    "depth of field": "景深",
    "bokeh": "散景",
    "chiaroscuro": "明暗对照",
    "film grain": "胶片颗粒",
    "color grading": "色彩分级",

    # quality/anime
    "anime style": "动漫风格",
    "cel shading": "赛璐珞上色",
    "manga style": "漫画风格",
    "light novel illustration": "轻小说插画",

    # character/hair colors
    "blonde hair": "金发",
    "white hair": "白发",
    "black hair": "黑发",
    "brown hair": "棕发",
    "red hair": "红发",
    "blue hair": "蓝发",
    "pink hair": "粉发",
    "green hair": "绿发",
    "silver hair": "银发",
    "purple hair": "紫发",
    "auburn hair": "赤褐色头发",
    "grey hair": "灰发",
    "orange hair": "橙发",
    "yellow hair": "黄发",
    "teal hair": "青绿发",
    "cyan hair": "青发",
    "maroon hair": "栗色头发",
    "indigo hair": "靛蓝发",
    "multicolored hair": "多彩发",

    # character/hair style
    "long hair": "长发",
    "short hair": "短发",
    "medium hair": "中长发",
    "bob cut": "波波头",
    "twin tails": "双马尾",
    "single tail": "单马尾",
    "ponytail": "马尾辫",
    "braids": "辫子",
    "curly hair": "卷发",
    "wavy hair": "波浪发",
    "straight hair": "直发",
    "bangs": "刘海",
    "side bangs": "侧刘海",
    "ahoge": "呆毛",
    "hair between eyes": "刘海遮眼",
    "shoulder-length hair": "肩长发",
    "broom bangs": "扫帚刘海",
    "drill hair": "卷发筒",
    "hime cut": "姬发式",

    # character/eyes
    "red eyes": "红眼",
    "blue eyes": "蓝眼",
    "green eyes": "绿眼",
    "grey eyes": "灰眼",
    "yellow eyes": "黄眼",
    "purple eyes": "紫眼",
    "pink eyes": "粉眼",
    "heterochromia": "异色瞳",

    # clothing
    "school uniform": "校服",
    "dress": "连衣裙",
    "skirt": "裙子",
    "pants": "裤子",
    "jacket": "夹克",
    "coat": "大衣",
    "hoodie": "连帽衫",
    "suit": "西装",
    "kimono": "和服",
    " Bikini": "比基尼",
    "overalls": "背带裤",
    "apron": "围裙",
    "vest": "背心",
    "blouse": "衬衫",
    "t-shirt": "T恤",
    "sweater": "毛衣",
    "robe": "长袍",
    "armor": "铠甲",
    "plate mail": "板甲",
    "leather armor": "皮甲",
    "maid outfit": "女仆装",
    "witch hat": "女巫帽",

    # scene
    "outdoor": "户外",
    "indoors": "室内",
    "city": "城市",
    "nature": "自然",
    "forest": "森林",
    "beach": "海滩",
    "mountain": "山",
    "sky": "天空",
    "sunset": "日落",
    "sunrise": "日出",
    "night": "夜晚",
    "daytime": "白天",
    "rain": "雨",
    "snow": "雪",
    "clouds": "云",
    "stars": "星星",
    "moonlight": "月光",
    "fire": "火",
    "water": "水",
    "flower": "花",
    "butterfly": "蝴蝶",
    "lightning": "闪电",

    # composition
    "close-up": "特写",
    "medium shot": "中景",
    "wide shot": "远景",
    "full body": "全身",
    "portrait": "半身像",
    "over the shoulder": "过肩镜头",
    "low angle": "低角度",
    "high angle": "高角度",
    "dutch angle": "荷兰角",
    "top-down": "俯视",
    "bird's eye view": "鸟瞰",
    "worm's eye view": "虫瞰",
    "rule of thirds": "三分法",
    "centered": "居中构图",
    "symmetry": "对称",

    # lighting
    "natural light": "自然光",
    "golden hour": "黄金时段",
    "blue hour": "蓝调时刻",
    "backlit": "逆光",
    "rim light": "轮廓光",
    "soft light": "柔光",
    "hard light": "硬光",
    "volumetric lighting": "体积光",
    "dappled light": "斑驳光影",
    "moonlight": "月光",
    "candlelight": "烛光",
    "neon light": "霓虹灯",
    "studio lighting": "摄影棚灯光",

    # styles
    "oil painting": "油画",
    "watercolor": "水彩",
    "pencil drawing": "铅笔画",
    "ink drawing": "水墨画",
    "pixel art": "像素艺术",
    "low poly": "低多边形",
    "3D render": "3D渲染",
    "vector art": "矢量艺术",
    "concept art": "概念艺术",
    "portrait painting": "肖像画",
    "landscape": "风景画",
    "anime": "动漫",
    "cartoon": "卡通",
    "realistic": "写实",
    "fantasy": "奇幻",
    "sci-fi": "科幻",
    "steampunk": "蒸汽朋克",
    "cyberpunk": "赛博朋克",
    "gothic": "哥特",
    "retro": "复古",
    "minimalist": "极简主义",
}


# ---------- file helpers ----------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_index():
    """Load the _translations.jsonl index."""
    index_path = os.path.join("keywords", TRANSLATIONS_INDEX)
    entries = []
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries


def save_index(entries):
    """Save the _translations.jsonl index."""
    index_path = os.path.join("keywords", TRANSLATIONS_INDEX)
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_all_keywords():
    """Load ALL keywords from all category files."""
    all_kws = []
    for fp in sorted(glob.glob("keywords/categories/*.json")):
        data = load_json(fp)
        for item in (data if isinstance(data, list) else [data]):
            item["_source_file"] = fp
            all_kws.append(item)
    return all_kws


def write_category_file(path, data):
    """Write back a category file, preserving format."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------- translation engine ----------

def build_index(entries):
    """Build a fast lookup: term_lower -> chinese_translation."""
    idx = {}
    for entry in entries:
        term = entry.get("term", "").lower()
        zh = entry.get("term_zh", "")
        if term and zh:
            idx[term] = zh
    return idx


def find_translation(term: str, index: dict) -> str:
    """Find Chinese translation for an English term.
    Priority: pre_translations > index > similar_match > None
    """
    lower = term.lower().strip()

    # 1. Pre-defined
    if lower in PRE_TRANSLATIONS:
        return PRE_TRANSLATIONS[lower]

    # 2. Index
    if lower in index:
        return index[lower]

    # 3. Fuzzy match
    best_sim = 0
    best_term = None
    for key in index:
        sim = SequenceMatcher(None, lower, key).ratio()
        if sim > best_sim and sim >= 0.85:
            best_sim = sim
            best_term = key

    if best_term:
        return index[best_term]

    return None


def collect_untranslated(all_kws):
    """Collect keywords that are missing term_zh."""
    untranslated = []
    for kw in all_kws:
        if not kw.get("term_zh"):
            untranslated.append(kw)
    return untranslated


def translate_batch(untranslated_kws, index):
    """Translate a batch of keywords. Returns (translated_items, untranslated_count)."""
    translated_count = 0
    for kw in untranslated_kws:
        term = kw.get("term", "").strip()
        if not term:
            continue

        zh = find_translation(term, index)
        if zh:
            kw["term_zh"] = zh
            kw["_translated_auto"] = True
            kw["_translated_at"] = datetime.now(timezone.utc).isoformat()
            translated_count += 1

    return translated_count


# ---------- interactive mode ----------

def interactive_translate(kw, index):
    """Ask user for translation of a single keyword."""
    term = kw.get("term", "")
    auto_zh = find_translation(term, index)

    print(f"\n[{kw.get('category', '?')}/{kw.get('subcategory', '?')}]")
    print(f"  term:   {term}")
    if auto_zh:
        print(f"  auto:   {auto_zh}  (enter to skip)")
    else:
        print(f"  auto:   (none found)")
    zh = input("  term_zh> ").strip()
    if zh:
        kw["term_zh"] = zh
        kw["_translated_manual"] = True
        kw["_translated_at"] = datetime.now(timezone.utc).isoformat()
        return True
    return False


# ---------- report ----------

def print_report(translated_count, skipped_count, total, file_counts):
    print("\n" + "=" * 60)
    print("  Translation Report")
    print("=" * 60)
    print(f"  Total keywords:     {total}")
    print(f"  Translated:         {translated_count}")
    print(f"  Untranslated:       {skipped_count}")
    if total:
        pct = translated_count / total * 100
        print(f"  Coverage:           {pct:.1f}%")
    print(f"\n  Files updated:")
    for fp, count in sorted(file_counts.items()):
        print(f"    {fp}: {count} keywords")
    print()


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="PWS Batch Translator")
    parser.add_argument("--translate-all", action="store_true", help="Translate all keyword files")
    parser.add_argument("--file", metavar="FILE", help="Translate a single file only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without writing")
    parser.add_argument("--generate-draft", metavar="FILE", help="Generate draft translation JSON for review")
    parser.add_argument("--interactive", action="store_true", help="Interactive manual translation mode")
    parser.add_argument("--force", action="store_true", help="Overwrite existing term_zh values")
    args = parser.parse_args()

    # Load existing translations index
    index_entries = load_index()
    index = build_index(index_entries)

    if args.generate_draft:
        # Generate draft for review
        kws = load_all_keywords() if not args.file else load_json(args.file)
        if isinstance(kws, dict):
            kws = [kws]

        draft = {"generated_at": datetime.now(timezone.utc).isoformat(), "entries": []}
        for kw in kws:
            term = kw.get("term", "").strip()
            if not term:
                continue
            zh = find_translation(term, index)
            if zh:
                draft["entries"].append({
                    "id": kw.get("id", ""),
                    "term": term,
                    "term_zh": zh,
                    "category": kw.get("category", ""),
                    "subcategory": kw.get("subcategory", ""),
                })

        os.makedirs(os.path.dirname(args.generate_draft) or ".", exist_ok=True)
        with open(args.generate_draft, "w", encoding="utf-8") as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)
        print(f"Draft written to {args.generate_draft} ({len(draft['entries'])} entries)")
        return

    # Load keywords
    if args.translate_all:
        all_kws = load_all_keywords()
    elif args.file:
        all_kws = load_json(args.file)
        if isinstance(all_kws, dict):
            all_kws = [all_kws]
        for kw in all_kws:
            kw["_source_file"] = args.file
    elif args.dry_run:
        # dry-run defaults to translate-all
        all_kws = load_all_keywords()
    else:
        print("Error: specify --translate-all or --file FILE", file=sys.stderr)
        sys.exit(1)

    # Filter untranslated
    if not args.force:
        kws_to_translate = [kw for kw in all_kws if not kw.get("term_zh")]
    else:
        kws_to_translate = all_kws

    if args.interactive:
        print(f"Interactive mode: {len(kws_to_translate)} keywords to translate\n")
        count = 0
        for kw in kws_to_translate:
            if interactive_translate(kw, index):
                count += 1
        print(f"\nManual translated: {count}/{len(kws_to_translate)}")
        return

    # Dry run mode
    if args.dry_run:
        # Make copies so we don't mutate originals
        copy_list = [dict(kw, _source_file=kw.get("_source_file", "")) for kw in kws_to_translate]
        translated_count = translate_batch(copy_list, index)
        print(f"DRY RUN: Would translate {translated_count}/{len(kws_to_translate)} keywords")

        # Show a sample (up to 15 translated ones)
        translated_samples = [kw for kw in copy_list if kw.get("term_zh")][:15]
        if translated_samples:
            print("\nSample translations:")
            for kw in translated_samples:
                print(f"  {kw.get('term')} -> {kw['term_zh']}")
        else:
            print("\n(Note: no auto-translations available in pre-defined dictionary)")
            print("Try: python3 tools/pws-translate.py --generate-draft output/draft.json")
        return

    # Full translate mode
    kw_list = list(kws_to_translate)
    translated_count = translate_batch(kw_list, index)
    skipped_count = len(kw_list) - translated_count

    # Save translation index
    for kw in kw_list:
        if kw.get("term_zh"):
            entry = {
                "term": kw.get("term", ""),
                "term_zh": kw["term_zh"],
                "id": kw.get("id", ""),
                "category": kw.get("category", ""),
                "updated_at": kw.get("_translated_at", datetime.now(timezone.utc).isoformat()),
            }
            # Only add if not already in index (avoid duplicates)
            existing_terms = {e["term"] for e in index_entries}
            if entry["term"] not in existing_terms:
                index_entries.append(entry)

    save_index(index_entries)

    # Write back to files
    file_counts = {}
    for kw in kw_list:
        if kw.get("term_zh"):
            src = kw.get("_source_file", "")
            if not src:
                continue
            file_counts[src] = file_counts.get(src, 0) + 1

            # Find and update in source data
            data = load_json(src)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if item.get("id") == kw.get("id"):
                        data[i]["term_zh"] = kw["term_zh"]
                        if kw.get("updated_at"):
                            data[i]["updated_at"] = kw["updated_at"]
                        break
                write_category_file(src, data)

    print_report(translated_count, skipped_count, len(kws_to_translate), file_counts)


if __name__ == "__main__":
    main()
