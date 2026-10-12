# Prompt Warehouse 规则

## 项目
- 路径：`/Users/ceasar/Documents/GitHub/prompt-warehouse`
- 数据：`keywords/categories/*.json`、`templates/_meta.json`
- 校验：`./scripts/validate-json.sh`
- 索引：`python3 tools/pws-index.py`

## 约束
- 禁止：截图、浏览器、URL
- 修改已有文件用 `str_replace`，不用 `write_file` 覆盖
- 版本号从 `keywords/_meta.json` 读，不硬编码
- 数量从 `keywords/_index.json` 读，不硬编码

## 关键词字段
必填：`id`、`term`、`term_zh`、`category`、`subcategory`
选填：`labels`、`labels_zh`、`score`、`priority`、`lifecycle`、`source`
`id` 格式：`{category}_{subcategory}_{slug}`

## 贡献流程
1. 修改 `keywords/categories/{category}.json`
2. 跑 `./scripts/validate-json.sh`
3. 跑 `python3 tools/pws-index.py`
4. 提交 PR

## 版本号规范
- 从 `1.0.0` 起步，不继承历史跳跃编号（v1.2.0 → v1.7.0 这类频繁跳号不再使用）
- **小更新**（字段补全、规则优化、文档修正）：只动最后一位，如 `1.0.x`
- **大幅度改动**（新增 API 端点、schema 变更、分类结构调整）：动中间位，如 `1.x.0`
- **破坏性变更**（现有数据格式/字段语义改变）：动第一位，如 `x.0.0`
- 版本号从 `keywords/_meta.json` 读取，不硬编码

## 汇报
必须报告：修改文件、校验输出、当前版本、`git log --oneline -3`
不要：截图、浏览器、URL

## 沟通
卡住超过 30 秒 → 主动报告"卡住"并停止