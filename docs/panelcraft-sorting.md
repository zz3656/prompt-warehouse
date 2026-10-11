# PanelCraft 排序建议

## 排序优先级

1. **负面词走独立通道**
   - 用 `is_negative: true` 识别（negative.json 中 103 条）
   - 不参与正面词排序
   - 固定附加到 prompt 末尾

2. **正面词按 weight 降序**
   - 用 `weight` 字段（0-1）
   - PanelCraft 排序时优先使用 weight

3. **同 weight 时按 score 降序**
   - weight 缺失时回退到 `score`

## 代码示例

```python
def rank_keywords(kws):
    """按 weight 排序，负面词分离。当前 compatibility 全显式绑定，无空值。"""
    negative = [k for k in kws if k.get("is_negative")]
    positive = [k for k in kws if not k.get("is_negative")]
    positive.sort(key=lambda k: (k.get("weight", 0), k.get("score", 0)), reverse=True)
    return positive, negative
```

## Compatibility 过滤

- **视频专用词**：12 条 `shot-language` 分类的镜头运动词，compatibility 仅含 `[kling, runway, minimax_h3]`
  - PanelCraft 生成图像时过滤掉这些词
  - 视频生成时保留

- **compatibility 现状**：当前所有关键词都有显式 compatibility，无空值。过滤时按模型精确匹配，不要假设空=通用。

## 权重设计说明

- `weight`：组合权重，与 score 解耦
  - PanelCraft 排序用 weight（有区分度）
  - score：质量评分，用于同 weight 时的次级排序

- `is_negative`：负面标记
  - negative.json 中 103 条，weight=0.5（不参与正面排序）
  - PanelCraft 应走独立通道，固定附加到 prompt 末尾

## Bundle 中的权重复用

- bundle 的 `keywords` 数组中，每个关键词可覆盖 weight：
  ```json
  {"id": "quality_basic_masterpiece", "weight": 0.9}
  ```
- PanelCraft 解析 bundle 时，bundle 中的 weight 覆盖全局默认值


## 更新（P1-4）

当前 6037 条全部有显式 compatibility，无空值。过滤时按模型精确匹配，不要假设空=通用。
