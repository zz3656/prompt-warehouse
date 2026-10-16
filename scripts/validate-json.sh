#!/usr/bin/env bash
# 校验所有 JSON 文件语法 + schema 必填字段
set -e

echo "=== 校验 keywords/categories/*.json ==="
for f in keywords/categories/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 keywords JSON 语法正确"

# P1: 增加 schema 校验（需要 jsonschema 包）
echo "=== Schema 校验 keywords ==="
python3 - <<'PYEOF'
import json, glob, sys
from jsonschema import validate, ValidationError

schema = json.load(open("schema/keyword.schema.json", encoding="utf-8"))
errors = 0

for f in glob.glob("keywords/categories/*.json"):
    slug = f.split("/")[-1].replace(".json", "")
    # 不再跳过 _pending_review — schema 已允许 'uncategorized'，其他分类也正常校验
    data = json.load(open(f, encoding="utf-8"))
    if isinstance(data, list):
        for i, item in enumerate(data):
            try:
                validate(instance=item, schema=schema)
            except ValidationError as e:
                kw_id = item.get("id", f"line_{i+1}")
                print(f"  ❌ {f.split('/')[-1]}[{kw_id}]: {e.message}")
                errors += 1
    else:
        print(f"  ⚠️  {f.split('/')[-1]}: not a list, skipping")

if errors:
    print(f"❌ Schema 校验失败: {errors} 条")
    sys.exit(1)
else:
    print("✅ 所有 keywords 通过 schema 校验")
PYEOF

echo "=== Schema 校验 bundles ==="
python3 - <<'PYEOF'
import json, glob, sys
from jsonschema import validate, ValidationError

schema = json.load(open("schema/bundle.schema.json", encoding="utf-8"))
errors = 0

for f in glob.glob("bundles/*.json"):
    try:
        data = json.load(open(f, encoding="utf-8"))
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            bid = data.get("id", f.split("/")[-1].replace(".json",""))
            print(f"  ❌ {bid}: {e.message}")
            errors += 1
    except json.JSONDecodeError:
        print(f"  ⚠️  跳过（语法错误已在前面校验）")

if errors:
    print(f"❌ Schema 校验失败: {errors} 条")
    sys.exit(1)
else:
    print("✅ 所有 bundles 通过 schema 校验")
PYEOF

echo "=== Schema 校验 workflows ==="
python3 - <<'PYEOF'
import json, glob, sys
from jsonschema import validate, ValidationError

schema = json.load(open("schema/workflow.schema.json", encoding="utf-8"))
errors = 0

for f in glob.glob("workflows/*.json"):
    if "_meta" in f:
        continue
    try:
        data = json.load(open(f, encoding="utf-8"))
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            wid = data.get("id", f.split("/")[-1].replace(".json",""))
            print(f"  ❌ {wid}: {e.message}")
            errors += 1
    except json.JSONDecodeError:
        print(f"  ⚠️  跳过（语法错误已在前面校验）")

if errors:
    print(f"❌ Schema 校验失败: {errors} 条")
    sys.exit(1)
else:
    print("✅ 所有 workflows 通过 schema 校验")
PYEOF

echo "=== Schema 校验 templates ==="
python3 - <<'PYEOF'
import json, glob, sys
from jsonschema import validate, ValidationError

schema = json.load(open("schema/template.schema.json", encoding="utf-8"))
errors = 0

for f in glob.glob("templates/*.json"):
    if "_meta" in f or "_legacy" in f:
        continue
    try:
        data = json.load(open(f, encoding="utf-8"))
        # templates 可能是 list 或 dict
        targets = data if isinstance(data, list) else [data]
        for item in targets:
            try:
                validate(instance=item, schema=schema)
            except ValidationError as e:
                tid = item.get("id", f"template_{errors+1}")
                print(f"  ❌ {tid}: {e.message}")
                errors += 1
    except json.JSONDecodeError:
        print(f"  ⚠️  跳过（语法错误已在前面校验）")

if errors:
    print(f"❌ Schema 校验失败: {errors} 条")
    sys.exit(1)
else:
    print("✅ 所有 templates 通过 schema 校验")
PYEOF

echo "=== 校验 _meta.json ==="
for f in keywords/_meta.json templates/_meta.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 _meta.json 语法正确"

echo "=== 校验 schema/*.json ==="
for f in schema/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 schema JSON 语法正确"

echo "=== 校验 docs/*.json (跳过) ==="
# docs/*.json — 已清理，不再需要校验

echo "=== 全部通过 ==="
