#!/usr/bin/env python3
"""Phase 1 (修正版): 清理 mj_v5* 过时前缀，重命名子分类并跨分类迁移。

与原版不同：此版本会正确地将关键词从源分类文件移动到目标分类文件，
确保每个分类文件中只包含 category 等于该文件名（不含.json）的条目。

用法: python3 tools/phase1-rename-mj-prefix.py [--dry-run]
"""

import json
import os
import sys
import glob
from collections import defaultdict


# 映射规则: (源分类, 旧子分类) → 新子分类
MAPPING_RULES = {
    # scene 相关 → scene.*
    ("scene", "mj_v5_nature"): "scene.nature",
    ("scene", "mj_v5_objects"): "scene.objects",
    ("scene", "mj_v5_geo"): "scene.geography",
    ("scene", "mj_v5_space"): "scene.space",
    # lighting 相关 → lighting.*
    ("lighting", "mj_v5_lighting"): "lighting.effects",
    ("lighting", "mj_v5_sfx"): "lighting.special",
    # clothing 相关 → clothing.*
    ("clothing", "mj_v5_materials"): "clothing.material",
    ("clothing", "mj_v5_matprops"): "clothing.material_props",
    # composition 相关 → camera.* (新分类)
    ("composition", "mj_v5_camera"): "camera.settings",
    ("composition", "mj_v5_structure"): "composition.structure",
    ("composition", "mj_v5_geometry"): "composition.geometry",
    ("composition", "mj_v5_perspective"): "camera.perspective",
    # styles 相关 → style.* (新分类) 或 color-look.*
    ("styles", "mj_v5_design"): "style.design",
    ("styles", "mj_v5_digital"): "style.digital",
    ("styles", "mj_v5_dimension"): "style.dimension",
    ("styles", "mj_v5_intangibles"): "style.intangibles",
    ("styles", "mj_v5_mediums"): "style.mediums",
    ("styles", "mj_v5_themes"): "style.themes",
    ("styles", "mj_v5_colors"): "color-look.palette",  # 配色归入 color-look
    ("styles", "mj_v5_colors2"): "color-look.palette",
    ("styles", "mj_v5_artists"): "style.artists",
}

# 从映射中推导新分类名（一级分类）
def get_target_category(new_sub: str) -> str:
    """从新子分类推导一级分类名。"""
    return new_sub.split(".")[0]


def rewrite_id_for_migration(old_id: str, target_category: str, new_subcategory: str) -> str:
    """根据迁移目标重写 id。"""
    parts = old_id.split("_")
    if len(parts) >= 3:
        slug = parts[-1]
        return f"{target_category}_{new_subcategory.replace('.', '_')}_{slug}"
    return old_id


def main():
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("=== DRY RUN 模式 — 不写入文件 ===\n")
    
    categories_dir = "keywords/categories"
    
    # 1. 收集所有分类文件中的关键词，按 (category, subcategory) 分组
    print("=== Phase 1: mj_v5* 前缀清理（修正版） ===\n")
    
    all_keywords = []  # (source_file, keyword_dict)
    
    for fpath in sorted(glob.glob(os.path.join(categories_dir, "*.json"))):
        cat_name = os.path.basename(fpath).replace(".json", "")
        if cat_name.startswith("_"):
            continue
        
        with open(fpath) as f:
            keywords = json.load(f)
        
        for kw in keywords:
            sub = kw.get("subcategory", "")
            
            # 检查是否匹配映射规则
            mapped = None
            for (old_cat, old_sub), new_sub in MAPPING_RULES.items():
                if cat_name == old_cat and sub == old_sub:
                    mapped = new_sub
                    break
            
            if mapped is not None:
                all_keywords.append((fpath, cat_name, kw, mapped))
    
    total_moved = len(all_keywords)
    print(f"需要迁移的关键词总数: {total_moved}")
    
    # 按目标分类分组
    by_target = defaultdict(list)  # target_category -> [(source_file, keyword)]
    
    for src_file, src_cat, kw, new_sub in all_keywords:
        target_cat = get_target_category(new_sub)
        by_target[target_cat].append((src_file, kw, new_sub))
    
    for target_cat in sorted(by_target.keys()):
        count = len(by_target[target_cat])
        print(f"  {target_cat}: {count} 条")
    
    if dry_run:
        print("\n(未写入文件，仅预览)")
        return
    
    # 2. 执行迁移：从源文件移除，添加到目标文件
    written_files = set()
    
    for target_cat, items in by_target.items():
        target_path = os.path.join(categories_dir, f"{target_cat}.json")
        
        # 读取现有目标文件（如果有）
        existing = []
        if os.path.exists(target_path):
            with open(target_path) as f:
                existing = json.load(f)
        
        existing_ids = set(kw.get("id") for kw in existing)
        
        # 添加新关键词（去重）
        added = 0
        for src_file, kw, new_sub in items:
            old_id = kw.get("id", "")
            new_id = rewrite_id_for_migration(old_id, target_cat, new_sub)
            
            # 更新关键词
            updated_kw = dict(kw)
            updated_kw["id"] = new_id
            updated_kw["category"] = target_cat  # 关键：更新 category 字段
            updated_kw["subcategory"] = new_sub
            
            # 更新 labels 中的 mj_v5* 前缀
            new_labels = []
            for label in updated_kw.get("labels", []):
                if "mj_v5" in str(label):
                    mapped_label = new_sub.replace(".", "_")
                    new_labels.append(mapped_label)
                else:
                    new_labels.append(label)
            updated_kw["labels"] = new_labels
            
            if new_id not in existing_ids:
                existing.append(updated_kw)
                existing_ids.add(new_id)
                added += 1
        
        # 写入目标文件
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
            f.write("\n")
        
        written_files.add(target_path)
        print(f"\n  {target_cat}.json: 新增 {added} 条 (现有 {len(existing)} 条)")
    
    # 3. 清理源文件：移除已迁移的关键词
    # 先收集所有需要迁移的 (source_file, kw_id) 对
    to_remove = defaultdict(set)  # source_file -> set of ids
    
    for fpath, cat_name, kw, new_sub in all_keywords:
        mapped = None
        for (old_cat, old_sub_pattern), new_sub_pattern in MAPPING_RULES.items():
            if cat_name == old_cat and kw.get("subcategory", "") == old_sub_pattern:
                mapped = new_sub_pattern
                break
        
        if mapped is not None:
            to_remove[fpath].add(kw.get("id"))
    
    # 从源文件移除已迁移的关键词
    for fpath, remove_ids in to_remove.items():
        if not remove_ids:
            continue
        
        with open(fpath) as f:
            keywords = json.load(f)
        
        remaining = [kw for kw in keywords if kw.get("id") not in remove_ids]
        cat_name = os.path.basename(fpath).replace(".json", "")
        print(f"  {cat_name}.json: {len(keywords)} → {len(remaining)} 条 (移除 {len(remove_ids)})")
        
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(remaining, f, ensure_ascii=False, indent=2)
            f.write("\n")
    
    # 4. 统计最终结果
    total = 0
    by_category = {}
    
    for f in sorted(glob.glob(os.path.join(categories_dir, "*.json"))):
        cat_name = os.path.basename(f).replace(".json", "")
        if cat_name.startswith("_"):
            continue
        
        with open(f) as fh:
            keywords = json.load(fh)
        
        count = len(keywords)
        by_category[cat_name] = count
        total += count
    
    print(f"\n=== 完成: 迁移 {total_moved} 条关键词 ===")
    print(f"总关键词数: {total}")
    print(f"分类数: {len(by_category)}")


if __name__ == "__main__":
    main()
