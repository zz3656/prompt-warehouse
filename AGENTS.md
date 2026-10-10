# Prompt Warehouse 规则

## 项目
- 路径：`/Users/ceasar/Documents/GitHub/prompt-warehouse`
- 数据：`keywords/categories/*.json`、`templates/_all_templates.json`
- 校验：`./scripts/validate-json.sh`
- 索引：`python3 scripts/generate-index.py`

## 约束
- 禁止：截图、浏览器、URL
- 修改已有文件用 `str_replace`，不用 `write_file` 覆盖
- 版本号从 `keywords/_meta.json` 读，不硬编码

## 关键词字段
必填：`id`、`term`、`term_zh`、`category`、`subcategory`
选填：`labels`、`labels_zh`、`score`、`priority`、`lifecycle`、`source`

`id` 格式：`{category}_{subcategory}_{slug}`

## 贡献流程
1. 修改 `keywords/categories/{category}.json`
2. 跑 `./scripts/validate-json.sh`
3. 跑 `python3 scripts/generate-index.py`
4. 提交 PR

## 汇报
必须报告：修改文件、校验输出、当前版本、`git log --oneline -3`
不要：截图、浏览器、URL

## 版本策略（重要）

**当前处于分类优化期间**：
- 版本号固定在 **1.0.0**
- **不要**在每次修改时升级版本
- 优化全部完成后，一次性升到 **1.1.0**

**日常修改**：
- 修正关键词：**不动版本号**（累积到下次 release）
- 新增关键词：**不动版本号**
- 只有正式 release 时才升级

**发布时**：
- PATCH +1：数据修正
- MINOR +1：新增功能
- MAJOR +1：破坏性变更

详细规则见 `VERSIONING.md`。

## 沟通
卡住超过 30 秒 → 主动报告"卡住"并停止