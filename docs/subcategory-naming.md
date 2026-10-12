# 子分类命名规范

> **pws v1.0.0**



## 命名规则

1. **格式**：小写 + 下划线或连字符，全仓库统一
2. **无前缀**：不带项目前缀（如 h3_、pwc_）
3. **Midjourney v5 前缀**：mj_v5_ 前缀的子分类（如 mj_v5_camera）通过 subcategory_group 分组

## 分组机制

- **subcategory**：实际子分类名，如 `mj_v5_camera`、`basic`
- **subcategory_group**：逻辑分组，如 `midjourney_v5`
- PanelCraft UI 按 subcategory_group 归类，不直接展示 mj_v5_ 前缀

## 当前 mj_v5_ 子分类分布

| 分类 | 唯一子分类数 | 子分类列表 |
|------|-------------|------------|
| clothing | 2 | mj_v5_materials, mj_v5_matprops |
| composition | 4 | mj_v5_camera, mj_v5_geometry, mj_v5_perspective, mj_v5_structure |
| lighting | 2 | mj_v5_lighting, mj_v5_sfx |
| scene | 4 | mj_v5_geo, mj_v5_nature, mj_v5_objects, mj_v5_space |
| styles | 9 | mj_v5_artists, mj_v5_colors, mj_v5_colors2, mj_v5_design, mj_v5_digital, mj_v5_dimension, mj_v5_intangibles, mj_v5_mediums, mj_v5_themes |

- 总条目涉及 mj_v5_: **3484**（占总数 ~58%）
- 唯一子分类数: **21**

## subcategory_group 规则

- 仅 mj_v5_* 前缀的子分类需要 `subcategory_group: "midjourney_v5"`
- 其他子分类不设 subcategory_group（或根据未来需要添加新分组）

## 示例

```json
{
    "id": "composition_mj_v5_camera",
    "term": "rule of thirds",
    "subcategory": "mj_v5_camera",
    "subcategory_group": "midjourney_v5"
}
```

PanelCraft 在 UI 中可将 subcategory_group="midjourney_v5" 的条目折叠到 "Midjourney V5" 分组下，subcategory 显示为去前缀后的名称（如 "camera"）。
