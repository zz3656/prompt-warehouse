# PWS 优化计划 v1.9

## 目标
优化仓库以便安全、标准化地进行增量更新。

## Phase 1 — 新增入库工具（最关键）
- 创建 `tools/pws-add-new.py`: 一键完成"去重检查 → 分类判定 → 合并 → 更新 _meta → 生成日志"
- 新增关键词标准模板 `templates/new_keyword_template.json`（含所有字段标注）
- 中文贡献指南 → 补充到 `ADD_PROMPTS_GUIDE.md` 的已有中文内容中

## Phase 2 — 字段补全
- 给所有 5,943 条补充缺失的 `created_at`（来源时间推算）
- 给所有 5,943 条补充 `updated_at` = 当前时间
- 基于已有 `notes` 中提取高价值词 → 补充 `aliases`
- 重新分级 `priority`: 从 notes 提取质量信号

## Phase 3 — 结构清理
- 清理 `tools/archive/extend-translations-*.py`（移到 git history 即可）
- 添加 `CONTRIBUTING_zh.md`

## 执行顺序
Phase 1 工具 → Phase 2 数据 → Phase 3 清理
