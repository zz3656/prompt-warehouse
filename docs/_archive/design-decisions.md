# Design Decisions — Prompt Warehouse

本文档记录 P0-P2 阶段的关键设计决策、教训和理由。供后续维护者参考。

---

## 1. P0 数据源选择决策

### 选定的数据源

| 数据源 | 类型 | 理由 |
|--------|------|------|
| **MiniMax H3** (awesome-minimax-h3-prompts) | 视频关键词 | MiniMax H3 是当前主流视频模型，其 prompt 库覆盖镜头运动、转场、时间效果等视频核心概念。导入脚本 `tools/import-minimax-h3.py` 已实现自动匹配和去重。 |
| **AI Camera Shots** (joost/ai-camera-shots) | 镜头术语 | 提供标准化 shot type / camera move / transition 分类，覆盖视频拍摄的完整语言体系。导入脚本 `tools/import-camera-shots.py` 已实现自动分类和增量导入。 |

### 放弃的数据源

| 数据源 | 原因 |
|--------|------|
| **shuixian** | 数据格式过于碎片化，条目间重复率高，且与 PWS 核心关键词体系重叠度低。导入脚本已归档至 `tools/_archive/import-shuixian.py`。 |
| **prompts.chat** | 纯英文社区 prompt，缺乏结构化分类和元数据，质量参差不齐。导入脚本已归档至 `tools/_archive/import-prompts-chat.py`。 |

### 视频模型兼容性策略

P0 阶段从 MiniMax H3 提取了 63 条视频专用术语，后续在 P1-1 中通过语义审查，将 **camera-motions、transitions、temporal、action-fx、panel、scene（部分）、lighting、color-look、composition** 共 1,659 条关键词的 `compatibility` 扩展为包含 `["kling", "runway", "minimax_h3"]`。

---

## 2. P2-2 字段命名教训

### 错误：term_zh → name_zh 统一重命名

**背景：** P2-2 审计时发现 keyword 使用 `term_zh`，而 bundle/template/workflow 使用 `name_zh`。误判为"命名不一致"，将 6,282 条关键词的 `term_zh` 重命名为 `name_zh`。

**问题：**
1. **语义不同**：`term_zh` 是术语翻译（如 "blonde hair" → "金发"），而 `name_zh` 是实体名称（如角色名、产品名）。两者语义不可互换。
2. **PanelCraft 依赖**：PanelCraft 中文检索模块依赖 `term_zh` 字段进行中文匹配。
3. **项目规范**：PWS 标准明确要求 `term_zh` 100% 覆盖（实际覆盖率达 98%）。

**教训：**
- **不要跨领域统一字段名**。即使表面看起来"命名不一致"，也需要先确认语义是否等价。
- **重命名前必须检查所有消费方**。包括 PanelCraft 等外部依赖。
- **发现错误后应立即回滚**，并记录教训（本文档）。

### 正确的命名规范

| 实体 | 术语翻译字段 | 实体名称字段 |
|------|-------------|-------------|
| keyword | `term_zh`（中文翻译） | `name_zh`（不适用，keyword 无独立名称） |
| template | `name_zh`（中文名称） | — |
| bundle | `name_zh`（中文名称） | — |
| workflow | `name_zh`（中文名称） | — |

**核心原则：** 只有需要"翻译"的实体用 `term_zh`，只有需要"命名"的实体用 `name_zh`。

---

## 3. 字段精简决策

### 从 keyword.schema.json 移除的字段

| 字段 | 原因 | 填充率 |
|------|------|--------|
| `success_rate` | 从未被任何关键词填充（0%） | 0% |
| `variations` | 从未被任何关键词填充（0%） | 0% |

### 其他被讨论但未移除的字段

| 字段 | 填充率 | 决策 |
|------|--------|------|
| `description` / `description_zh` | 0% | 保留在 schema 中（未使用，但语义有用，未来可能启用） |
| `priority` | — | 已移除（不在 schema 中，P0 阶段未使用） |
| `tags` | — | bundle/template 中使用，keyword 中不使用（语义不同） |
| `aliases` / `alias_of` | ~2% | 保留（用于同义重复的 canonical 管理） |
| `score` | 100% | 保留（P1-3 的 score_v2 系统基于此） |
| `weight` | 100% | 保留（Bundle 组合排序使用） |

---

## 4. 增量导入调度

### 推荐调度频率

- **每周一次**：对 MiniMax H3 和 AI Camera Shots 进行增量检查。
- **手动触发**：`python3 tools/pws-import.py <source>`

### 运行方式

```bash
# 查看帮助
python3 tools/pws-import.py --help

# 检查并导入新版本（自动跳过未更新源）
python3 tools/pws-import.py minimax-h3

# 强制导入（跳过版本检查）
python3 tools/pws-import.py minimax-h3 --force

# 仅检查，不写入
python3 tools/pws-import.py minimax-h3 --dry-run

# 审计 _pending_review 状态
python3 tools/pws-import.py audit

# 生成待审核报告
python3 tools/pws-import.py report
```

### 导入流程

1. **版本检查**：`pws-import.py` 读取 `keywords/_meta.json` 中记录的 `last_commit`，与本地仓库最新 commit 比较。
2. **跳过或导入**：版本一致则跳过；版本更新则调用对应导入脚本。
3. **增量处理**：导入脚本自动过滤已存在的 term，只输出新条目。
4. **审核流程**：新条目写入 `keywords/categories/_pending_review.json`，由人工审核后：
   - 确认入库 → 移动到对应 `categories/{category}.json`
   - 拒绝 → 从 `_pending_review.json` 中移除

### 版本检查机制

- **Git commit hash**：通过 `git rev-parse HEAD` 获取上游仓库最新 commit。
- **元数据持久化**：commit hash 写入 `keywords/_meta.json` 的 `imports.{source}.last_commit`。
- **首次导入**：无记录时，直接执行完整导入（假设上游为最新版本）。

### 归档数据源

`prompts-chat` 和 `shuixian` 两个已弃用数据源的导入脚本已归档至：
- `tools/_archive/import-prompts-chat.py`
- `tools/_archive/import-shuixian.py`

如需恢复，可从归档目录复制回 `tools/` 根目录。
