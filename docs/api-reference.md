# PWS API 参考

静态 API 通过 GitHub Pages 托管，PanelCraft 和其他调用方通过 HTTP GET 读取 JSON 数据。

**基础 URL**: `https://zz3656.github.io/api/`

---

## 端点列表

| 端点 | 文件 | 说明 |
|------|------|------|
| `/stats.json` | [API](https://zz3656.github.io/api/stats.json) | 全局统计（关键词数、分类数、score 分布等） |
| `/categories.json` | [API](https://zz3656.github.io/api/categories.json) | 分类列表 + 子分类 + 每个分类的关键词数 |
| `/workflows.json` | [API](https://zz3656.github.io/api/workflows.json) | 所有工作流列表 |
| `/bundles.json` | [API](https://zz3656.github.io/api/bundles.json) | 所有配方包列表（id/name/category/keyword_count） |
| `/bundle_{id}.json` | [API](https://zz3656.github.io/api/bundle_character_animesque_portrait.json) | 单个配方包完整内容（`{id}` 中的 `.` 和 `-` 替换为 `_`） |
| `/index.json` | [API](https://zz3656.github.io/api/index.json) | API 入口（所有端点索引） |

---

## 数据源

- **关键词**: `https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/keywords/`
- **模板**: `https://cdn.jsdelivr.net/gh/zz3656/prompt-warehouse@main/templates/`

---

## 更新机制

每次 push 到 `main` 分支时，GitHub Actions 自动运行 `generate-api.py` 重新生成所有 API 文件。

---

## 示例调用

```bash
# 获取全局统计
curl https://zz3656.github.io/api/stats.json

# 获取分类列表
curl https://zz3656.github.io/api/categories.json

# 获取单个配方包
curl https://zz3656.github.io/api/bundle_character_animesque_portrait.json
```
