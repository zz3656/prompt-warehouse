# Archived: extend-translations history

> 归档日期: 2026-09-30
> 原因: 这 13 个 one-shot 脚本中的所有翻译条目 (9122 条) 已合并到 `tools/pws-translate.py` 的 `PRE_TRANSLATIONS` dict 中。这些脚本已无运行价值，仅作为历史迁移记录保留。

## 文件清单

| 脚本 | 条目数 | 说明 |
|------|------:|------|
| `extend-translations.py`     | ~430 | 初始翻译批次 |
| `extend-translations-2.py`   | ~800 | 服装/穿着类模式 |
| `extend-translations-3.py`   | ~640 | 场景/灯光扩展 |
| `extend-translations-4.py`   | ~530 | 风格/艺术扩展 |
| `extend-translations-5.py`   | ~890 | 通用词汇扩展 |
| `extend-translations-6.py`   | ~670 | 修饰词扩展 |
| `extend-translations-7.py`   | ~2040 | 综合批次（最大） |
| `extend-translations-8.py`   | ~750 | 摄影/镜头类 |
| `extend-translations-9.py`   | ~480 | 情感/氛围类 |
| `extend-translations-10.py`  | ~330 | 摄影/色彩/角色/取景 |
| `extend-translations-11.py`  | ~570 | 场景/风格/负面/材质 |
| `extend-translations-12.py`  | ~110 | 截断 60-char 复合词 |
| `extend-translations-13.py`  | ~60 | 最终批（v1.0.0 100% 覆盖达成） |

## 验证

```bash
# 当前所有翻译都在 pws-translate.py 中
python3 -c "import re; src=open('tools/pws-translate.py').read(); m=re.search(r'PRE_TRANSLATIONS\s*=\s*\{(.*?)\n\}\n', src, re.S); print('PRE_TRANSLATIONS entries:', len(re.findall(r'\"[^\"]+\":\s*\"', m.group(1))))"
# => PRE_TRANSLATIONS entries: 9122
```

## 不要再使用

请直接修改 `tools/pws-translate.py` 中的 `PRE_TRANSLATIONS` dict，或在 issue 中提议新条目。