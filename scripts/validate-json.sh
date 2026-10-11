#!/usr/bin/env bash
# 校验所有 JSON 文件语法 + schema 必填字段
set -e

echo "=== 校验 keywords/categories/*.json ==="
for f in keywords/categories/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 keywords JSON 语法正确"

echo "=== 校验 templates/*.json ==="
for f in templates/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 templates JSON 语法正确"

echo "=== 校验 bundles/*.json ==="
for f in bundles/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 bundles JSON 语法正确"

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

echo "=== 校验 docs/*.json ==="
for f in docs/*.json; do
    python3 -c "import json; json.load(open('$f', encoding='utf-8'))" || { echo "❌ $f"; exit 1; }
done
echo "✅ 所有 docs JSON 语法正确"

echo "=== 全部通过 ==="
