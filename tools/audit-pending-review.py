#!/usr/bin/env python3
"""audit-pending-review.py — 审计 _pending_review.json，筛除纯文本类提示词。

判定标准：
  keep: 描述视觉特征（颜色/光影/构图/风格/场景/角色外观）
  discard: 以动词开头（Act/Write/Explain/Summarize...）或描述抽象任务
  uncertain: 不确定，保留但标记 review_status="uncertain"

一次性脚本，已执行完毕，请勿重复运行。
"""

import json
import os
import re
import sys

INPUT_FILE = "keywords/categories/_pending_review.json"
OUTPUT_FILE = "keywords/categories/_pending_review.json"
DISCARDED_FILE = "keywords/categories/_discarded_prompts_chat.json"

# 文本类提示词特征：以这些动词/短语开头，通常表示角色扮演或任务指令
TEXT_PATTERNS = [
    r"^\s*act\s+as\b",           # Act as...
    r"^\s*i\s+want\s+you\s+to\s+",  # I want you to...
    r"^\s*pretend\s+to\b",       # Pretend to...
    r"^\s*imagine\s+you\s+are\b", # Imagine you are...
    r"^\s*you\s+are\s+an?\s*",    # You are a/an...
    r"^\s*roleplay\b",            # Roleplay...
    r"^\s*simulate\s+as?\s*",     # Simulate as...
    r"^\s*be\s+an?\s*",           # Be a/an...
]

# 任务型动词开头（非视觉描述）
TASK_VERBS = [
    r"^\s*write\s+(a|an|the)?\s",
    r"^\s*create\s+(a|an|the)?\s",
    r"^\s*generate\s+(a|an|the)?\s",
    r"^\s*make\s+(a|an|the)?\s",
    r"^\s*design\s+(a|an|the)?\s",
    r"^\s*build\s+(a|an|the)?\s",
    r"^\s*develop\s+(a|an|the)?\s",
    r"^\s*produce\s+(a|an|the)?\s",
    r"^\s*explain\s+(a|an|the)?\s",
    r"^\s*summarize\b",
    r"^\s*summarise\b",
    r"^\s*translate\b",
    r"^\s*list\b",
    r"^\s*provide\s+(a|an|the)?\s",
    r"^\s*tell\s+me\b",
    r"^\s*give\s+(a|an|the)?\s",
    r"^\s*show\s+me\b",
    r"^\s*help\s+me\b",
    r"^\s*teach\s+me\b",
    r"^\s*i\s+need\b",
    r"^\s*i\s+would\s+like\b",
    r"^\s*explain\s+(a|an|the)?\s",
    r"^\s*analyze\b",
    r"^\s*compare\b",
    r"^\s*identify\b",
    r"^\s*implement\b",
    r"^\s*code\b",
    r"^\s*program\b",
    r"^\s*code\s+a\b",
    r"^\s*program\s+a\b",
    r"^\s*build\s+an?\s+(app|website|api)",
    r"^\s*create\s+a\s*prompt",
    r"^\s*i\s+wanna\b",
    r"^\s*i\s+want\b",
]

# 视觉/图像相关关键词（命中 → 可能是 keep）
VISUAL_KEYWORDS = [
    "portrait", "face", "character", "person", "woman", "man", "girl", "boy",
    "child", "headshot", "avatar", "figure", "model", "subject",
    "light", "glow", "shadow", "shadows", "illumination", "bloom",
    "volumetric", "cinematic light", "natural light", "studio lighting",
    "backlit", "rim light", "ambient light", "lighting", "brightness",
    "contrast", "hdr", "high dynamic",
    "shot", "camera", "angle", "lens", "view", "perspective",
    "framing", "close-up", "closeup", "medium shot", "wide angle",
    "fisheye", "macro", "bokeh", "depth of field", "dof",
    "panoramic", "aerial", "drone", "bird's eye", "low angle",
    "high angle", "dutch angle", "tilt-shift", "isometric",
    "style", "render", "art", "painting", "illustration", "sketch",
    "drawing", "watercolor", "oil painting", "anime", "manga",
    "realistic", "photorealistic", "surreal", "abstract",
    "minimalist", "baroque", "rococo", "impressionism",
    "cubism", "pop art", "art deco", "pixel art", "chibi",
    "concept art", "digital art", "vector art", "3d render",
    "flat design", "resolution", "8k", "4k", "ultra hd",
    "color", "colors", "colour", "colours", "gradient", "palette",
    "texture", "material", "fabric", "metal", "stone", "wood",
    "forest", "ocean", "mountain", "city", "building", "room",
    "garden", "beach", "desert", "snow", "rain", "storm",
    "smoke", "fire", "water", "waterfall", "river", "lake",
    "flower", "flowers", "tree", "trees", "plant", "leaves",
    "clothing", "dress", "shirt", "jacket", "coat", "suit",
    "makeup", "cosmetic", "beauty", "fashion", "outfit",
    "photograph", "photo", "image", "picture", "canvas",
    "sculpture", "statue", "figurine", "puppet", "mask",
    "sunset", "sunrise", "golden hour", "twilight", "dusk",
    "night", "dark", "bright", "vintage", "retro", "futuristic",
    "cyberpunk", "steampunk", "fantasy", "sci-fi", "horror",
    "romantic", "dramatic", "ethereal", "dreamy", "mysterious",
    "elegant", "graceful", "powerful", "serene", "chaotic",
    "detailed", "intricate", "minimal", "simple", "complex",
    "film", "movie", "cinema", "animation", "cartoon", "comic",
    "meme", "gif", "video", "scene", "background", "foreground",
    "prop", "product", "object", "icon", "logo", "stamp", "map",
    "graphic", "infographic", "poster", "banner", "flyer",
    "magazine", "cover", "album", "record", "vinyl",
    "neon", "led", "laser", "sparkle", "spark", "flame",
    "blur", "sharp", "focus", "exposure", "iso",
    "perspective", "vanishing point", "horizon", "skyline",
    "interior", "exterior", "architecture", "landscape",
    "street", "urban", "rural", "industrial", "suburban",
    "furniture", "kitchen", "bathroom", "bedroom", "living room",
    "shoes", "boots", "hat", "cap", "scarf", "glasses",
    "jewelry", "necklace", "bracelet", "ring", "earring",
    "armor", "weapon", "sword", "shield", "bow", "arrow",
    "car", "vehicle", "truck", "bike", "motorcycle", "boat",
    "airplane", "spaceship", "robot", "cyborg", "alien",
    "angel", "demon", "ghost", "zombie", "vampire", "werewolf",
    "unicorn", "dragon", "phoenix", "griffin", "hydra",
    "cloud", "mist", "fog", "rainbow", "aurora", "galaxy",
    "star", "moon", "sun", "planet", "comet", "nebula",
    "crystal", "gem", "diamond", "ruby", "emerald", "pearl",
    "candle", "lantern", "torch", "candlelight", "flicker",
    "mirror", "reflection", "watermark", "graffiti", "mural",
    "tapestry", "wallpaper", "postcard", "bookmark", "ticket",
    "passport", "badge", "medal", "trophy", "award",
]

# 视频/动画相关（可能是 keep）
VIDEO_KEYWORDS = [
    "video", "animation", "animated", "cinematic", "film",
    "motion", "moving", "sequence", "scene", "clip", "reel",
    "timelapse", "slow motion", "stop motion", "frame",
]


def is_visual_or_video(term: str) -> bool:
    """检查 term 是否包含视觉/图像/视频相关关键词。"""
    text = term.lower()
    import re
    for kw in VISUAL_KEYWORDS:
        if re.search(r'(?<!\w)' + re.escape(kw) + r'(?!\w)', text):
            return True
    for kw in VIDEO_KEYWORDS:
        if re.search(r'(?<!\w)' + re.escape(kw) + r'(?!\w)', text):
            return True
    return False


def is_text_prompt(term: str) -> bool:
    """检查 term 是否是文本类提示词（角色扮演/任务指令）。"""
    text = term.lower()

    # 检查 Act as / I want you to 等模式
    for pattern in TEXT_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True

    # 检查任务型动词开头
    for pattern in TASK_VERBS:
        if re.match(pattern, text, re.IGNORECASE):
            return True

    # 包含 "prompt" 但描述的是 prompt 生成而非视觉内容
    if re.search(r"create\s+(a|an)?\s*prompt", text) and not is_visual_or_video(text):
        return True

    return False


def classify_term(term: str) -> tuple:
    """分类单条：(decision, reason)。"""
    text = term.lower()

    # 1. 文本类提示词 → discard
    if is_text_prompt(text):
        reason = "text-prompt"
        return ("discard", reason)

    # 2. 视觉/图像/视频相关 → keep
    if is_visual_or_video(text):
        reason = "visual-content"
        return ("keep", reason)

    # 3. 无法确定 → uncertain
    reason = "uncertain-need-review"
    return ("uncertain", reason)


def reclassify_uncategorized(kw: dict):
    """对 keep 且 uncategorized 的条目尝试重新映射分类。"""
    term = kw["term"].lower()

    # 使用单词边界匹配，避免 "hat" 误匹配 "chat"
    def has_word(text, words):
        for w in words:
            # 使用单词边界：词首、词尾或前后有空格/标点
            import re
            if re.search(r'(?<!\w)' + re.escape(w) + r'(?!\w)', text):
                return True
        return False

    category_rules = {
        "character": [
            "portrait", "face", "character", "person", "people", "woman",
            "man", "girl", "boy", "child", "headshot", "avatar",
            "figure", "model", "subject", "cosplay", "puppet", "mask",
        ],
        "lighting": [
            "light", "glow", "shadow", "shadows", "illumination", "bloom",
            "volumetric", "cinematic light", "natural light", "studio lighting",
            "backlit", "rim light", "ambient light", "lighting", "brightness",
            "contrast", "hdr", "high dynamic",
        ],
        "composition": [
            "shot", "camera", "angle", "lens", "view", "perspective",
            "framing", "close-up", "closeup", "medium shot", "wide angle",
            "fisheye", "macro", "bokeh", "depth of field", "dof",
            "panoramic", "aerial", "drone", "bird's eye", "low angle",
            "high angle", "dutch angle", "tilt-shift", "isometric",
        ],
        "styles": [
            "style", "render", "art", "painting", "illustration", "sketch",
            "drawing", "watercolor", "oil painting", "anime", "manga",
            "realistic", "photorealistic", "surreal", "abstract",
            "minimalist", "baroque", "rococo", "impressionism",
            "cubism", "pop art", "art deco", "pixel art", "chibi",
            "concept art", "digital art", "vector art", "3d render",
            "flat design", "resolution", "8k", "4k", "ultra hd",
            "vintage", "retro", "futuristic", "cyberpunk", "steampunk",
            "fantasy", "sci-fi", "horror", "romantic", "dramatic",
            "ethereal", "dreamy", "mysterious", "elegant", "graceful",
            "powerful", "serene", "chaotic", "detailed", "intricate",
            "minimal", "simple", "complex", "cartoon", "comic",
            "photo", "photograph", "image", "picture", "canvas",
            "sculpture", "statue", "figurine", "makeup", "cosmetic",
            "beauty", "fashion", "outfit", "dress", "shirt", "jacket",
            "coat", "suit", "clothing", "fabric", "metal", "stone",
            "wood", "glass", "ceramic", "jewelry", "necklace",
            "armor", "weapon", "sword", "shield", "bow", "arrow",
            "car", "vehicle", "truck", "bike", "motorcycle", "boat",
            "airplane", "spaceship", "robot", "cyborg", "alien",
            "angel", "demon", "ghost", "zombie", "vampire",
            "unicorn", "dragon", "phoenix", "griffin", "hydra",
            "cloud", "mist", "fog", "rainbow", "aurora", "galaxy",
            "star", "moon", "sun", "planet", "comet", "nebula",
            "crystal", "gem", "diamond", "ruby", "emerald", "pearl",
            "candle", "lantern", "torch", "candlelight", "flicker",
            "mirror", "reflection", "watermark", "graffiti", "mural",
            "tapestry", "wallpaper", "postcard", "bookmark", "ticket",
            "passport", "badge", "medal", "trophy", "award",
            "map", "graphic", "infographic", "poster", "banner",
            "flyer", "magazine", "cover", "album", "record", "vinyl",
            "neon", "led", "laser", "sparkle", "spark", "flame",
            "blur", "sharp", "focus", "exposure", "iso",
            "perspective", "vanishing point", "horizon", "skyline",
            "interior", "exterior", "architecture", "landscape",
            "street", "urban", "rural", "industrial", "suburban",
            "furniture", "kitchen", "bathroom", "bedroom", "living room",
            "shoes", "boots", "hat", "cap", "scarf", "glasses",
            "film", "movie", "cinema", "animation", "animated",
            "motion", "moving", "sequence", "scene", "clip", "reel",
            "timelapse", "slow motion", "stop motion", "frame",
            "video", "gif", "meme", "product", "object", "icon",
            "logo", "stamp", "flag", "map", "chart", "graph",
            "tree", "trees", "plant", "leaves", "flower", "flowers",
            "forest", "ocean", "mountain", "city", "building", "room",
            "garden", "beach", "desert", "snow", "rain", "storm",
            "smoke", "fire", "water", "waterfall", "river", "lake",
            "sunset", "sunrise", "golden hour", "twilight", "dusk",
            "night", "dark", "bright", "gradient", "palette",
            "texture", "material", "background", "foreground",
        ],
    }

    for category, keywords in category_rules.items():
        if has_word(term, keywords):
            kw["category"] = category
            return

    # 仍无法映射 → 标记 needs_category
    kw["review_status"] = "needs_category"


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total entries to audit: {len(data)}")

    keep = []
    discard = []
    uncertain = []

    for kw in data:
        term = kw["term"]
        decision, reason = classify_term(term)

        if decision == "discard":
            kw_copy = dict(kw)
            kw_copy["audit_reason"] = reason
            discard.append(kw_copy)

        elif decision == "keep":
            # 处理 uncategorized → 尝试重新映射
            if kw.get("category") == "uncategorized":
                reclassify_uncategorized(kw)

            kw["review_status"] = "verified"
            keep.append(kw)

        elif decision == "uncertain":
            # 不确定但非文本类，保留并标记
            # uncategorized 也要过一遍文本检查（之前漏掉了）
            if is_text_prompt(kw["term"]):
                kw_copy = dict(kw)
                kw_copy["audit_reason"] = "text-prompt (leaked)"
                discard.append(kw_copy)
                continue

            # 额外文本类检测：包含常见文本提示词特征但不匹配已知分类
            text_term = kw["term"].lower()
            text_signals = [
                r"let's\s+speak",
                r"for\s+the\s+sake\s+o'",
                r"i'd\s+like\s+to\s+analyze",
                r"give\s+me\s+(a|an|the)?\s*(summary|note|info)",
                r"how\s+it\s+is",
                r"bias\s+implementation",
                r"draft\s+a\s+\d",
                r"an?\s+rfq\s+email",
                r"be\s+concise",
                r"chatgpt\s+(pro|plan)",
            ]
            import re as re_mod
            for sig in text_signals:
                if re_mod.search(sig, text_term):
                    kw_copy = dict(kw)
                    kw_copy["audit_reason"] = "text-prompt (signal match)"
                    discard.append(kw_copy)
                    continue

            # 处理 uncategorized → 尝试重新映射
            if kw.get("category") == "uncategorized":
                reclassify_uncategorized(kw)

            kw["review_status"] = "uncertain"
            uncertain.append(kw)

    # 写入 _pending_review.json（keep + uncertain）
    output_data = keep + uncertain
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 写入 _discarded_prompts_chat.json
    with open(DISCARDED_FILE, "w", encoding="utf-8") as f:
        json.dump(discard, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 统计分类分布
    cat_dist = {}
    for kw in output_data:
        c = kw["category"]
        cat_dist[c] = cat_dist.get(c, 0) + 1

    # 打印报告
    print(f"\n{'=' * 60}")
    print("AUDIT REPORT")
    print(f"{'=' * 60}")
    print(f"Total entries:       {len(data)}")
    print(f"Kept (verified):     {len(keep)}")
    print(f"Uncertain:           {len(uncertain)}")
    print(f"Discarded:           {len(discard)}")

    print(f"\nCategory distribution (kept + uncertain):")
    for cat in sorted(cat_dist.keys()):
        print(f"  {cat:20s}: {cat_dist[cat]}")

    print(f"\nUncategorized handling:")
    uncat_count = sum(1 for kw in output_data if kw["category"] == "uncategorized")
    needs_cat = sum(1 for kw in output_data if kw.get("review_status") == "needs_category")
    print(f"  Still uncategorized: {uncat_count}")
    print(f"  Marked needs_category: {needs_cat}")

    # discard 抽样 5 条
    print(f"\nDiscarded samples (5):")
    for i, d in enumerate(discard[:5], 1):
        print(f"  {i}. [{d['audit_reason']}] {d['term'][:100]}")

    # keep 抽样 5 条
    print(f"\nKept samples (5):")
    for i, k in enumerate(keep[:5], 1):
        print(f"  {i}. [{k.get('category')}] (reason={k.get('review_status')}) {k['term'][:100]}")

    print(f"\nOutput files:")
    print(f"  Kept: {OUTPUT_FILE} ({len(output_data)} entries)")
    print(f"  Discarded: {DISCARDED_FILE} ({len(discard)} entries)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
