#!/usr/bin/env python3
"""
pws-generate-labels-zh — 基于分类和 term_zh 生成 labels_zh

为每个关键词自动生成中文搜索标签：
1. 从 term_zh 提取前 3 个有意义的词（去停用词）
2. 从 subcategory 添加分类标签
3. 从 source 添加来源标签（如 nodaro）

Usage:
  python3 tools/pws-generate-labels-zh.py --dry-run
  python3 tools/pws-generate-labels-zh.py --apply
"""

import argparse
import glob
import json
import re
import sys
from datetime import datetime, timezone


# Chinese stop words (common words to skip when extracting labels)
STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就",
    "不", "人", "都", "一", "一个", "上", "也", "很",
    "到", "说", "要", "去", "你", "会", "着", "没有",
    "看", "好", "自己", "这", "他", "她", "它", "们",
    "那", "哪些", "什么", "哪个", "哪里", "怎么", "如何",
    "而", "与", "及", "等", "之", "其", "所", "为",
}

# Subcategory -> Chinese label mapping
SUBCATEGORY_LABELS = {
    # quality
    "basic": "基础", "advanced": "高级", "technical": "技术",
    "anime": "动漫", "animeSpecific": "动漫专用",
    "texture": "纹理", "composition": "构图",
    "color": "色彩", "atmosphere": "氛围",
    # character
    "hair": "发型", "hairColors": "发色",
    "eyes": "眼睛", "eyeColors": "瞳色",
    "expression": "表情", "pose": "姿势",
    "mood": "情绪", "anatomy": "解剖",
    "bodyType": "体型", "body": "身体",
    "skin": "肤色", "age": "年龄",
    "clothing": "服装", "accessories": "配饰",
    "effects": "特效", "detail": "细节",
    "face": "面部", "character": "角色",
    # clothing
    "tops": "上衣", "bottoms": "下装",
    "outfits": "套装", "accessories": "配饰",
    "mj_v5_materials": "材质", "mj_v5_matprops": "材质属性",
    "wardrobe-archetype": "服装原型", "wardrobe-top": "上装",
    "wardrobe-bottom": "下装", "wardrobe-outerwear": "外套",
    "wardrobe-footwear": "鞋履", "wardrobe-headwear": "头饰",
    "wardrobe-accessories": "配件",
    "wardrobe-color-palette": "配色", "wardrobe-material": "面料",
    "wardrobe-era": "年代",
    # composition
    "framing": "画幅", "angles": "角度",
    "lens": "镜头", "camera-format": "画幅格式",
    "camera-motions": "运镜", "rules": "规则",
    "mj_v5_camera": "相机", "mj_v5_structure": "结构",
    "mj_v5_perspective": "透视", "mj_v5_geometry": "几何",
    "mj_v5_lighting": "灯光", "mj_v5_sfx": "特效光",
    "mj_v5_design": "设计", "mj_v5_digital": "数字",
    "mj_v5_mediums": "媒介", "mj_v5_themes": "主题",
    "mj_v5_colors": "色彩", "mj_v5_colors2": "色彩2",
    "mj_v5_dimension": "维度", "mj_v5_intangibles": "抽象",
    "mj_v5_artists": "艺术家",
    "mj_v5_nature": "自然", "mj_v5_objects": "物体",
    "mj_v5_geo": "地形", "mj_v5_space": "空间",
    "mj_v5_materials": "材质", "mj_v5_matprops": "材质属性",
    "mj_v5_perspective": "透视", "mj_v5_geometry": "几何",
    # lighting
    "natural": "自然光", "dramatic": "戏剧光",
    "mood": "氛围光", "dynamic": "动态光",
    "special": "特殊光", "mj_v5_lighting": "灯光",
    "mj_v5_sfx": "特效光", "atmosphere": "大气",
    # styles
    "art": "艺术", "aesthetic": "美学",
    "animeManga": "动漫漫画", "artStyles": "艺术风格",
    "artistStyle": "艺术家风格", "specialty": "专业",
    "realism": "写实",
    "mj_v5_design": "设计", "mj_v5_digital": "数字",
    "mj_v5_mediums": "媒介", "mj_v5_themes": "主题",
    "mj_v5_colors": "色彩", "mj_v5_colors2": "色彩2",
    "mj_v5_dimension": "维度", "mj_v5_intangibles": "抽象",
    "mj_v5_artists": "艺术家",
    # negative
    "quality": "质量缺陷", "anatomy": "解剖缺陷",
    "face": "面部缺陷", "composition": "构图缺陷",
    "style": "风格缺陷", "textRelated": "文字",
    "commonDefects": "常见缺陷",
    # scene
    "nature": "自然", "interaction": "交互",
    "weather": "天气", "time": "时间",
    "relationship": "关系", "indoor": "室内",
    "urban": "城市", "fantastical": "奇幻",
    "backdrop": "背景",
    "mj_v5_nature": "自然", "mj_v5_objects": "物体",
    "mj_v5_geo": "地形", "mj_v5_space": "空间",
    # panel
    "panelLayout": "分镜布局", "comicEffects": "漫画特效",
    "animation": "动画", "panelMood": "分镜氛围",
    # others
    "action-fx": "动作特效", "disaster": "灾害",
    "fire-blasts": "火焰", "electric": "电力",
    "combat": "战斗", "magic": "魔法",
    "sci-fi": "科幻", "misc": "杂项",
    "character-fx": "角色特效", "aura-ambient": "光环",
    "transformation": "变身", "power": "力量",
    "body-mod": "改造", "face-expression": "面部表情",
    "color-look": "色彩", "film-emulation": "胶片模拟",
    "palette": "调色板", "social-preset": "预设",
    "post-process": "后期",
    "photographer": "摄影师", "editorial": "编辑",
    "illustrator": "插画师", "concept": "概念",
    "documentary": "纪实", "cinematographer": "电影摄影师",
    "genre": "类型",
    "render-quality": "渲染", "other": "其他",
    "engines": "引擎", "resolution": "分辨率",
    "technical": "技术", "stamps": "印章",
    "era": "时代", "pre-modern": "前现代",
    "speculative": "推测", "decade-20c": "二十世纪",
    "framing": "构图", "shot-size": "景别",
    "composition": "构图", "coverage": "覆盖",
    "angle": "角度", "vantage": "视角",
    "held-prop": "手持道具", "occupational": "职业",
    "device": "设备", "drink": "饮品",
    "reading-writing": "读写", "smoking": "吸烟",
    "floral-nature": "花草自然", "companion": "伙伴",
    "instrument": "乐器",
    "material": "材质", "fabric": "织物",
    "metal": "金属", "stone": "石材",
    "wood": "木材", "exotic": " exotic",
    "natural": "天然", "glass-ceramic": "玻璃陶瓷",
    "transitions": "转场", "element": "元素",
    "standard": "标准", "portal": "门户",
    "physics": "物理", "morph": "变形",
    "glitch": "故障", "time": "时间",
    "light": "光线", "speed": "速度",
    "shutter": "快门", "freeze": "冻结",
    "direction": "方向",
    "temporal": "时间效果",
    "action-fx": "动作特效",
}


def extract_labels_from_term_zh(term_zh):
    """Extract meaningful Chinese words from term_zh as labels."""
    # Remove common suffixes and connectors
    text = term_zh.strip()
    # Remove trailing modifiers
    text = re.sub(r"(的|了|着|过|吗|呢|吧)$", "", text)
    # Tokenize by common separators
    tokens = re.split(r"[，,；;、\s]+", text)
    # Filter: keep words 2-4 chars, not stop words
    labels = []
    seen = set()
    for t in tokens:
        if 2 <= len(t) <= 4 and t not in STOP_WORDS and t not in seen:
            labels.append(t)
            seen.add(t)
        if len(labels) >= 3:
            break
    return labels


def get_source_tag(source):
    """Extract a Chinese tag from source field."""
    if not source:
        return None
    source_lower = source.lower()
    if "nodaro" in source_lower:
        return "nodaro"
    if "midjourney" in source_lower or "willwulfken" in source_lower:
        return "mj"
    if "danbooru" in source_lower or "civitai" in source_lower:
        return "danbooru"
    return None


def generate_labels_zh(item):
    """Generate labels_zh for a single keyword."""
    labels = []

    # Category names (dedicated dict, separate from SUBCATEGORY_LABELS)
    cat_names = {
        "quality": "质量", "composition": "构图", "lighting": "灯光",
        "character": "角色", "clothing": "服装", "styles": "风格",
        "negative": "负面", "scene": "场景", "panel": "分镜",
        "action-fx": "动作特效", "character-fx": "角色特效",
        "color-look": "色彩", "era": "时代", "framing": "构图",
        "held-prop": "手持道具", "material": "材质",
        "photographer": "摄影", "render-quality": "渲染",
        "temporal": "时间效果", "transitions": "转场",
    }
    cat = item.get("category", "")

    # 1. From category name (insert first)
    cat_name = cat_names.get(cat, "")
    if cat_name:
        labels.insert(0, cat_name)

    # 2. From subcategory
    sub = item.get("subcategory", "")
    if sub and sub in SUBCATEGORY_LABELS:
        sub_label = SUBCATEGORY_LABELS[sub]
        if sub_label not in labels:
            labels.insert(1, sub_label)

    # 3. From term_zh
    term_zh = item.get("term_zh", "")
    if term_zh:
        zh_labels = extract_labels_from_term_zh(term_zh)
        for zl in zh_labels:
            if zl not in labels:
                labels.append(zl)

    # 4. From source
    src_tag = get_source_tag(item.get("source", ""))
    if src_tag and src_tag not in labels:
        labels.append(src_tag)

    return labels


def main():
    parser = argparse.ArgumentParser(description="Generate labels_zh for keywords")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--file", metavar="FILE", help="Process only one file")
    args = parser.parse_args()

    total = 0
    updated = 0
    file_counts = {}

    files = glob.glob("keywords/categories/*.json")
    if args.file:
        files = [args.file]

    for fp in sorted(files):
        data = json.load(open(fp))
        if not isinstance(data, list):
            data = [data]

        file_changes = 0
        for item in data:
            if not item.get("labels_zh"):
                # Only generate labels_zh for items that have term_zh
                # (guarantees all labels are Chinese)
                if not item.get("term_zh"):
                    total += 1
                    continue
                labels_zh = generate_labels_zh(item)
                if labels_zh:
                    if args.dry_run or args.apply:
                        item["labels_zh"] = labels_zh
                        item["_labels_zh_generated"] = True
                        item["_generated_at"] = datetime.now(timezone.utc).isoformat()
                        file_changes += 1
                        updated += 1
                    total += 1
            else:
                total += 1

        if updated > 0 or (args.dry_run and file_changes > 0):
            if args.apply:
                json.dump(data, open(fp, "w"), ensure_ascii=False, indent=2)
                with open(fp, "a") as f:
                    f.write("\n")
            file_counts[fp] = file_changes

    print("=" * 60)
    print("  labels_zh Generation Report")
    print("=" * 60)
    print(f"  Keywords processed:  {total}")
    print(f"  Labels_zh generated: {updated}")
    if total:
        print(f"  Coverage:            {updated/total*100:.1f}%")
    if file_counts:
        print(f"\n  Files updated:")
        for fp, count in sorted(file_counts.items()):
            print(f"    {fp}: {count}")
    print()

    if args.dry_run:
        print("💡 Dry run — use --apply to write changes")


if __name__ == "__main__":
    main()
