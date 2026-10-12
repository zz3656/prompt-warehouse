#!/usr/bin/env python3
"""import-camera-shots.py — 从 joost/ai-camera-shots 提取镜头类型、运镜和转场术语。

数据来源: joost/ai-camera-shots (GitHub)
依赖: 仅标准库

# 一次性脚本，已执行完毕，请勿重复运行。
"""

import glob
import hashlib
import json
import os
import re
import sys


SHUIXIAN_DIR = "/tmp/ai-camera-shots"

OUTPUT_DIR = "keywords/categories"
PENDING_FILE = os.path.join(OUTPUT_DIR, "_pending_review.json")

# 34 种镜头类型（按 distance/height/facing/lens/movement 分组）
SHOT_TYPES = [
    "wide shot", "medium shot", "close-up", "macro", "eye-level",
    "low-angle", "high-angle", "dutch angle", "overhead", "aerial",
    "ground-level", "worm's-eye view", "profile", "three-quarter",
    "rear view", "over-the-shoulder", "POV", "selfie",
    "wide-angle close-up", "fisheye", "fisheye close-up",
    "overhead fisheye", "high-angle close-up", "low-angle close-up",
    "foreground occlusion", "foreground focus", "background focus",
    "silhouette", "prism reflection", "lens flare", "magnifying glass",
    "inside a hole", "hoop-level", "inside-the-fridge"
]

# 27 种运镜术语（movement）
CAMERA_MOVES = [
    "static camera", "locked-off", "push-in", "dolly in", "pull-out",
    "dolly out", "truck", "track", "follow", "lead", "pan",
    "tilt", "orbit", "arc", "crane", "pedestal", "drone", "FPV",
    "handheld", "whip pan", "rack focus", "crash zoom", "roll",
    "slow motion", "speed ramp", "dolly zoom", "vertigo effect"
]

# 33 种转场术语（transitions）
TRANSITIONS = [
    "pull-out reveal", "push-in", "crash zoom", "push through a portal",
    "rack focus", "roll", "object wipe", "body wipe", "whip pan",
    "lens block", "dip to dark", "portal", "screen wipe",
    "arc continuation", "roll continuation", "match cut", "smash cut",
    "filled-frame entry", "cut on action", "exit and enter frame",
    "fade in", "fade out", "dissolve", "iris", "graphic wipe",
    "J cut", "L cut", "sound bridge", "hidden cut", "generated bridge",
    "first and last frame", "last-frame handoff", "match on the smallest shared shape"
]

# 停用词（纯通用词，无实际图像意义）
STOPWORDS = {
    "POV", "FPV", "pan", "tilt", "roll", "arc", "drone", "track",
    "follow", "lead", "fade in", "fade out", "dissolve", "iris",
    "J cut", "L cut", "slow motion", "static camera", "locked-off",
}


def classify_shot_type(term: str) -> tuple[str, str]:
    """镜头类型 → (category, subcategory)。"""
    shot_to_sub = {
        "wide shot": "shot-size", "medium shot": "shot-size",
        "close-up": "shot-size", "macro": "shot-size",
        "eye-level": "angles", "low-angle": "angles", "high-angle": "angles",
        "dutch angle": "angles", "overhead": "aerial", "aerial": "aerial",
        "ground-level": "angles", "worm's-eye view": "angles",
        "profile": "shot-language", "three-quarter": "shot-language",
        "rear view": "shot-language", "over-the-shoulder": "shot-language",
        "POV": "shot-language", "selfie": "shot-language",
        "wide-angle close-up": "shot-size", "fisheye": "lens",
        "fisheye close-up": "lens", "overhead fisheye": "aerial",
        "high-angle close-up": "angles", "low-angle close-up": "angles",
        "foreground occlusion": "shot-language", "foreground focus": "focus-pull",
        "background focus": "focus-pull", "silhouette": "lighting",
        "prism reflection": "vfx", "lens flare": "lighting",
        "magnifying glass": "vfx", "inside a hole": "shot-language",
        "hoop-level": "angles", "inside-the-fridge": "shot-language",
    }
    sub = shot_to_sub.get(term.lower(), term.lower())
    return ("composition", sub)


def classify_camera_move(term: str) -> tuple[str, str]:
    """运镜术语 → (category, subcategory)。"""
    move_to_sub = {
        "static camera": "stabilized", "locked-off": "stabilized",
        "push-in": "push-in", "dolly in": "push-in", "pull-out": "pull-out",
        "dolly out": "pull-out", "truck": "tracking", "track": "tracking",
        "follow": "tracking", "lead": "tracking", "pan": "panning",
        "tilt": "tilting", "orbit": "orbiting", "arc": "orbiting",
        "crane": "crane", "pedestal": "crane", "drone": "aerial",
        "FPV": "aerial", "handheld": "handheld", "whip pan": "whip-pan",
        "rack focus": "focus-pull", "crash zoom": "zoom-in",
        "roll": "rotation", "slow motion": "slow-motion",
        "speed ramp": "speed-ramp", "dolly zoom": "zoom-in",
        "vertigo effect": "zoom-in"
    }
    sub = move_to_sub.get(term.lower(), term.lower())
    return ("composition", sub)


def classify_transition(term: str) -> tuple[str, str]:
    """转场术语 → (category, subcategory)。"""
    trans_to_sub = {
        "pull-out reveal": "reveal", "push-in": "push-in",
        "crash zoom": "zoom-in", "push through a portal": "portal",
        "rack focus": "focus-pull", "roll": "rotation",
        "object wipe": "wipe", "body wipe": "wipe", "whip pan": "whip-pan",
        "lens block": "fade-out", "dip to dark": "fade-out",
        "portal": "portal", "screen wipe": "wipe",
        "arc continuation": "seamless", "roll continuation": "seamless",
        "match cut": "jump-cut", "smash cut": "jump-cut",
        "filled-frame entry": "fade-out", "cut on action": "hard-cut",
        "exit and enter frame": "hard-cut", "fade in": "fade-in",
        "fade out": "fade-out", "dissolve": "cross-dissolve",
        "iris": "fade-out", "graphic wipe": "wipe",
        "J cut": "audio-led", "L cut": "audio-trail",
        "sound bridge": "audio-bridge", "hidden cut": "seamless",
        "generated bridge": "morph", "first and last frame": "morph",
        "last-frame handoff": "seamless",
        "match on the smallest shared shape": "jump-cut"
    }
    sub = trans_to_sub.get(term.lower(), term.lower())
    return ("transitions", sub)


def make_id(category: str, term: str) -> str:
    """生成 id: {category}_camerashots_{md5(term)[:8]}"""
    md5 = hashlib.md5(term.encode("utf-8")).hexdigest()[:8]
    return f"{category}_camerashots_{md5}"


def load_existing_terms() -> tuple[set[str], set[str]]:
    """加载现有 PWS 库中所有 term 和 term_zh。"""
    existing_terms = set()
    existing_zh = set()
    for f in sorted(glob.glob("keywords/categories/*.json")):
        basename = os.path.basename(f)
        if basename in ("_pending_review.json", "term_zh_supplement.json"):
            continue
        with open(f) as fh:
            data = json.load(fh)
        for kw in data:
            t = (kw.get("term") or "").strip().lower()
            tz = (kw.get("term_zh") or "").strip().lower()
            if t:
                existing_terms.add(t)
            if tz:
                existing_zh.add(tz)
    return existing_terms, existing_zh


def main():
    repo_dir = "/tmp/ai-camera-shots"
    print(f"[load] Loading existing PWS terms (term + term_zh)...")
    existing_terms, existing_zh = load_existing_terms()
    print(f"[load] Existing terms: {len(existing_terms)}, existing term_zh: {len(existing_zh)}")

    # 合并所有术语
    all_terms = []
    type_labels = []  # (term, category_type: shot/camera/transition)

    for t in SHOT_TYPES:
        all_terms.append(t.lower())
        type_labels.append((t, "shot"))
    for t in CAMERA_MOVES:
        all_terms.append(t.lower())
        type_labels.append((t, "camera"))
    for t in TRANSITIONS:
        all_terms.append(t.lower())
        type_labels.append((t, "transition"))

    print(f"\n[extraction] Total terms from resource: {len(type_labels)}")
    print(f"  Shot types: {len(SHOT_TYPES)}")
    print(f"  Camera moves: {len(CAMERA_MOVES)}")
    print(f"  Transitions: {len(TRANSITIONS)}")

    # 过滤：长度 2-50，非停用词，不与现有 PWS term 重复
    filter_stats = {"existing": 0, "stopword": 0, "length": 0}
    unique_terms = []  # (original_term, category_type)

    for orig, ctype in type_labels:
        t = orig.lower()
        if len(orig) < 2 or len(orig) > 50:
            filter_stats["length"] += 1
            continue
        if t in STOPWORDS:
            filter_stats["stopword"] += 1
            continue
        if t in existing_terms:
            filter_stats["existing"] += 1
            continue
        unique_terms.append((orig, ctype))

    print(f"\nFiltered out: existing={filter_stats['existing']}, stopword={filter_stats['stopword']}, length={filter_stats['length']}")
    print(f"Unique valid terms: {len(unique_terms)}")

    # 构建新条目
    new_items = []
    supplement_items = []

    for orig, ctype in unique_terms:
        if ctype == "shot":
            pws_category, subcategory = classify_shot_type(orig)
        elif ctype == "camera":
            pws_category, subcategory = classify_camera_move(orig)
        else:
            pws_category, subcategory = classify_transition(orig)

        # 检查是否 term_zh 已存在
        is_supplement = False
        if orig.lower() in existing_zh:
            for f in sorted(glob.glob("keywords/categories/*.json")):
                basename = os.path.basename(f)
                if basename in ("_pending_review.json", "term_zh_supplement.json"):
                    continue
                with open(f) as fh:
                    data = json.load(fh)
                for kw in data:
                    if (kw.get("term_zh") or "").strip().lower() == orig.lower():
                        supplement_items.append({
                            "existing_id": kw["id"],
                            "term_zh": orig,
                        })
                        is_supplement = True
                        break
                if is_supplement:
                    break

        if not is_supplement:
            kw = {
                "id": make_id(pws_category, orig),
                "term": orig,
                "term_zh": "",
                "category": pws_category,
                "subcategory": subcategory,
                "weight": 0.6,
                "score": 0.6,
                "source": "joost/ai-camera-shots",
                "compatibility": ["sdxl", "midjourney", "flux", "kling", "runway", "minimax_h3"],
                "is_negative": False,
                "needs_review": True,
            }
            new_items.append(kw)

    # 写入 _pending_review.json（追加到现有条目）
    print(f"\n[output] Writing {len(new_items)} new candidates to {PENDING_FILE}")
    existing_pending = []
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE) as f:
            existing_pending = json.load(f)
    merged_pending = existing_pending + new_items
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_pending, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 统计报告
    new_unique = len(new_items)

    print("\n" + "=" * 60)
    print("AI CAMERA SHOTS IMPORT REPORT")
    print("=" * 60)
    print(f"Resource files: 3 (shot-types.md, camera-moves.md, transitions.md)")
    print(f"Shot types: {len(SHOT_TYPES)}")
    print(f"Camera moves: {len(CAMERA_MOVES)}")
    print(f"Transitions: {len(TRANSITIONS)}")
    print(f"Filtered out: existing={filter_stats['existing']}, stopword={filter_stats['stopword']}, length={filter_stats['length']}")
    print(f"Matched to existing PWS term_zh: {len(supplement_items)}")
    print(f"New candidates (needs_review): {new_unique}")

    # 检查产出规模
    if 30 <= new_unique <= 150:
        print(f"\n✓ Within target range (30-150)")
    elif new_unique > 150:
        print(f"\n⚠️ Above max 150 ({new_unique} candidates)")
    else:
        print(f"\n⚠️ Below min 30 (only {new_unique})")

    # 按类型分布
    print("\nType distribution (new candidates):")
    type_dist = {}
    for kw in new_items:
        # 从 id 推断类型（camerashots → shot/camera/transition 无法直接判断）
        # 但我们知道 new_items 的构造逻辑，这里用 subcategory 推断
        pass

    # 按分类分布
    print("\nCategory distribution (new candidates):")
    cat_dist = {}
    subcat_dist = {}
    for kw in new_items:
        c = kw["category"]
        s = kw.get("subcategory", "unknown")
        cat_dist[c] = cat_dist.get(c, 0) + 1
        subcat_dist[s] = subcat_dist.get(s, 0) + 1

    for cat in sorted(cat_dist.keys()):
        print(f"  {cat:20s}: {cat_dist[cat]}")

    print("\nSubcategory distribution:")
    for sub in sorted(subcat_dist.keys()):
        print(f"  {sub:25s}: {subcat_dist[sub]}")

    # Top terms
    print(f"\nTop 30 terms by term name:")
    for kw in sorted(new_items, key=lambda x: x["term"])[:30]:
        print(f"  {kw['term']}: category={kw['category']}, subcategory={kw.get('subcategory')}")

    print(f"\nOutput file: {PENDING_FILE} ({len(new_items)} new candidates)")
    print("=" * 60)


if __name__ == "__main__":
    main()
