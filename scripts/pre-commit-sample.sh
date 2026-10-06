#!/usr/bin/env bash
# pre-commit hook: validate PWS data before commit
set -e

echo "🔍 PWS pre-commit validation..."

# Check if jsonschema is available (may not be installed locally)
HAS_JSONSCHEMA=true
python3 -c "import jsonschema" 2>/dev/null || HAS_JSONSCHEMA=false

# 1. Check no new files were added without .gitignore
if git diff --cached --diff-filter=ACM --name-only | grep -qE '\.pyc$|__pycache__|\.tmp$'; then
    echo "❌ Blocked: Files matching .gitignore patterns detected"
    git diff --cached --diff-filter=ACM --name-only | grep -E '\.pyc$|__pycache__|\.tmp$'
    exit 1
fi

# 2. Validate JSON syntax
echo "📝 Validating JSON syntax..."
for f in $(git diff --cached --diff-filter=ACM --name-only | grep '\.json$' || true); do
    if ! python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        echo "❌ Invalid JSON: $f"
        exit 1
    fi
done

# 3. Validate keyword schema (skip if jsonschema not installed)
if git diff --cached --name-only | grep -q 'keywords/categories/'; then
    if [ "$HAS_JSONSCHEMA" = true ]; then
        echo "📐 Validating keyword schema..."
        python3 - <<'PYEOF'
import json, glob, sys
from jsonschema import validate, ValidationError
schema = json.load(open("schema/keyword.schema.json"))
errors = []
for fp in sorted(glob.glob("keywords/categories/*.json")):
    for item in json.load(open(fp)):
        try:
            validate(instance=item, schema=schema)
        except ValidationError as e:
            errors.append(f"{fp}: id={item.get('id','?')} - {e.message}")
if errors:
    for e in errors[:10]:
        print(f"  ❌ {e}")
    sys.exit(1)
print(f"  ✅ Schema valid")
PYEOF
    else
        echo "⚠️  Skipping schema validation (jsonschema not installed)"
    fi
fi

# 4. Check ID pattern for changed files
if git diff --cached --name-only | grep -q 'keywords/categories/'; then
    echo "🔢 Checking ID patterns..."
    python3 - <<'PYEOF'
import json, glob, re, sys
pattern = re.compile(r'^[a-z][a-z0-9_]*$')
issues = []
for fp in sorted(glob.glob("keywords/categories/*.json")):
    for item in json.load(open(fp)):
        if not pattern.match(item.get("id", "")):
            issues.append(f"{fp}: {item['id']}")
if issues:
    for i in issues[:10]:
        print(f"  ❌ {i}")
    sys.exit(1)
print(f"  ✅ All IDs valid")
PYEOF
fi

# 5. Check term_zh coverage on staged files
echo "🌍 Checking term_zh coverage..."
python3 - <<'PYEOF'
import json, glob, sys
all_missing = []
total = 0
staged = set()
try:
    staged = set(
        line.strip()
        for line in __import__("subprocess").check_output(
            ["git", "diff", "--cached", "--diff-filter=ACM", "--name-only"],
            stderr=__import__("subprocess").DEVNULL
        ).decode().splitlines()
    )
except Exception:
    pass

missing_count = 0
for fp in sorted(glob.glob("keywords/categories/*.json")):
    data = json.load(open(fp))
    for item in data:
        total += 1
        if not item.get("term_zh"):
            missing_count += 1
            if not staged or fp in staged:
                all_missing.append(f"{fp}: {item.get('id')}")
if missing_count:
    print(f"  ⚠️  {missing_count}/{total} keywords missing term_zh")
    for m in all_missing[:5]:
        print(f"    - {m}")
else:
    print(f"  ✅ 100% term_zh coverage: {total}/{total}")
PYEOF

# 6. Quick dedup check on staged files only (fast mode)
staged_files=$(git diff --cached --diff-filter=ACM --name-only | grep 'keywords/categories/' || true)
if [ -n "$staged_files" ]; then
    echo "🔄 Checking staged files for duplicates..."
    python3 - <<PYEOF
import json, glob, sys, os
staged_files_list = """$staged_files""".strip().split() if "$staged_files".strip() else []
staged_items = []
for fp in staged_files_list:
    if not os.path.exists(fp):
        continue
    data = json.load(open(fp))
    if isinstance(data, list):
        staged_items.extend(data)
    else:
        staged_items.append(data)
# Load all existing keywords
existing_items = []
for fp in sorted(glob.glob("keywords/categories/*.json")):
    if fp not in staged_files_list:
        data = json.load(open(fp))
        if isinstance(data, list):
            existing_items.extend(data)
        else:
            existing_items.append(data)
# Check by ID
existing_ids = {i.get("id","") for i in existing_items if i.get("id")}
new_ids = {i.get("id","") for i in staged_items if i.get("id")}
conflicts = new_ids & existing_ids
if conflicts:
    for c in sorted(conflicts):
        print(f"  ❌ ID conflict: {c}")
    sys.exit(1)
print(f"  ✅ No conflicts with existing keywords")
PYEOF
fi

echo "✅ All checks passed!"
exit 0
