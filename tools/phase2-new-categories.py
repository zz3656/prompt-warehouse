#!/usr/bin/env python3
"""Phase 2: 创建 AI 漫剧专用新分类，并从现有文件迁移关键词。

新增分类:
- animation.json: 从 transitions.json (element/portal/morph) + temporal.json (speed/freeze/frame-rate) 迁移
- storyboard.json: 从 panel.json (animation/comiceffects/panellayout/panelmood) 迁移
- consistency.json: 新建（角色一致性、场景统一性关键词）
- video.json: 新建（IP-Adapter Video / AnimateDiff 相关）
- text_rendering.json: 新建（对话框文字/拟声词/效果字）

用法: python3 tools/phase2-new-categories.py [--dry-run]
"""

import json
import os
import sys
import glob
from datetime import datetime, timezone


def rewrite_id_for_new_category(old_id: str, new_category: str, new_subcategory: str) -> str:
    """从旧 id 推导新 id。"""
    parts = old_id.split("_")
    if len(parts) >= 3:
        slug = parts[-1]
        return f"{new_category}_{new_subcategory.replace('.', '_')}_{slug}"
    return old_id


def migrate_keywords(source_file: str, target_category: str, target_subcategories: list, 
                    new_subcat_map: dict) -> list:
    """从源文件迁移关键词到新分类。"""
    categories_dir = "keywords/categories"
    source_path = os.path.join(categories_dir, source_file)
    
    with open(source_path) as f:
        keywords = json.load(f)
    
    migrated = []
    
    for kw in keywords:
        sub = kw.get("subcategory", "")
        
        if sub not in target_subcategories:
            continue
        
        # 获取新的子分类（可能映射到多个）
        new_sub = new_subcat_map.get(sub, sub)
        
        # 更新 id 和 category
        old_id = kw.get("id", "")
        new_id = rewrite_id_for_new_category(old_id, target_category, new_sub)
        
        # 更新 labels
        new_labels = []
        for label in kw.get("labels", []):
            if str(label) in target_subcategories:
                mapped_label = new_sub.replace(".", "_")
                new_labels.append(mapped_label)
            else:
                new_labels.append(label)
        
        # 更新关键词
        updated_kw = dict(kw)
        updated_kw["id"] = new_id
        updated_kw["category"] = target_category
        updated_kw["subcategory"] = new_sub
        updated_kw["labels"] = new_labels
        
        migrated.append(updated_kw)
    
    return migrated


def create_empty_category(filepath: str):
    """创建空分类文件。"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)


def main():
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("=== DRY RUN 模式 — 不写入文件 ===\n")
    
    categories_dir = "keywords/categories"
    
    print("=== Phase 2: 新增 AI 漫剧专用分类 ===\n")
    
    # 1. animation.json — 从 transitions + temporal 迁移
    anim_keywords = migrate_keywords(
        "transitions.json", "animation",
        ["element", "portal", "morph"],
        {"element": "animation.element", "portal": "animation.portal", "morph": "animation.morph"}
    )
    
    temporal_path = os.path.join(categories_dir, "temporal.json")
    with open(temporal_path) as f:
        temporal = json.load(f)
    
    for kw in temporal:
        sub = kw.get("subcategory", "")
        if sub in ("speed", "freeze", "frame-rate"):
            old_id = kw.get("id", "")
            new_id = rewrite_id_for_new_category(old_id, "animation", "animation.frame")
            
            new_labels = []
            for label in kw.get("labels", []):
                if str(label) in ("speed", "freeze", "frame-rate"):
                    new_labels.append("animation.frame")
                else:
                    new_labels.append(label)
            
            updated_kw = dict(kw)
            updated_kw["id"] = new_id
            updated_kw["category"] = "animation"
            updated_kw["subcategory"] = "animation.frame"
            updated_kw["labels"] = new_labels
            anim_keywords.append(updated_kw)
    
    print(f"\nanimation.json: {len(anim_keywords)} 条关键词")
    
    # 2. storyboard.json — 从 panel 迁移
    sb_keywords = migrate_keywords(
        "panel.json", "storyboard",
        ["animation", "comiceffects", "panellayout", "panelmood"],
        {
            "animation": "storyboard.animation",
            "comiceffects": "storyboard.effect",
            "panellayout": "storyboard.layout",
            "panelmood": "storyboard.mood"
        }
    )
    
    print(f"storyboard.json: {len(sb_keywords)} 条关键词")
    
    # 3. consistency.json — 新建空文件（等待后续补充）
    print("consistency.json: 待补充（角色一致性关键词）")
    
    # 4. video.json — 新建空文件（等待后续补充）
    print("video.json: 待补充（视频生成关键词）")
    
    # 5. text_rendering.json — 新建空文件（等待后续补充）
    print("text_rendering.json: 待补充（文字渲染关键词）")
    
    # 执行写入（非 dry_run）
    if not dry_run:
        # 写入 animation.json
        anim_path = os.path.join(categories_dir, "animation.json")
        with open(anim_path, "w", encoding="utf-8") as f:
            json.dump(anim_keywords, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\n  写入: {anim_path}")
        
        # 写入 storyboard.json
        sb_path = os.path.join(categories_dir, "storyboard.json")
        with open(sb_path, "w", encoding="utf-8") as f:
            json.dump(sb_keywords, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  写入: {sb_path}")
        
        # 创建空分类文件
        for cat_name in ["consistency", "video", "text_rendering"]:
            cat_path = os.path.join(categories_dir, f"{cat_name}.json")
            create_empty_category(cat_path)
            print(f"  创建: {cat_path}")
        
        # 更新 panel.json — 移除已迁移的关键词（保留其他子分类的）
        with open(os.path.join(categories_dir, "panel.json")) as f:
            panel = json.load(f)
        
        remaining_panel = [kw for kw in panel 
                          if kw.get("subcategory", "") not in ("animation", "comiceffects", "panellayout", "panelmood")]
        
        with open(os.path.join(categories_dir, "panel.json"), "w", encoding="utf-8") as f:
            json.dump(remaining_panel, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  更新: panel.json (剩余 {len(remaining_panel)} 条)")
        
        # 更新 transitions.json — 移除已迁移的关键词（保留其他子分类的）
        with open(os.path.join(categories_dir, "transitions.json")) as f:
            transitions = json.load(f)
        
        remaining_trans = [kw for kw in transitions 
                          if kw.get("subcategory", "") not in ("element", "portal", "morph")]
        
        with open(os.path.join(categories_dir, "transitions.json"), "w", encoding="utf-8") as f:
            json.dump(remaining_trans, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  更新: transitions.json (剩余 {len(remaining_trans)} 条)")
        
        # 更新 temporal.json — 移除已迁移的关键词（保留其他子分类的）
        with open(temporal_path) as f:
            temporal = json.load(f)
        
        remaining_temp = [kw for kw in temporal 
                         if kw.get("subcategory", "") not in ("speed", "freeze", "frame-rate")]
        
        with open(temporal_path, "w", encoding="utf-8") as f:
            json.dump(remaining_temp, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  更新: temporal.json (剩余 {len(remaining_temp)} 条)")
    
    print(f"\n=== Phase 2 完成 ===")


if __name__ == "__main__":
    main()
