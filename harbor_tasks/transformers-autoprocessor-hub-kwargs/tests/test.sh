#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/models/auto/processing_auto.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.33
WEIGHTS[regression]=0.24
WEIGHTS[structural]=0.19
WEIGHTS[antistub]=0.19
WEIGHTS[config_ruff]=0.05

for key in behavioral regression structural antistub config_ruff; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (35%): Behavioral - hub kwargs are not filtered out ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()

# The bug: using inspect.signature(cached_file).parameters to filter kwargs
# The fix: using an explicit tuple of valid hub kwargs

# Check that inspect.signature is NOT used to build cached_file_kwargs
if "inspect.signature(cached_file)" in source:
    print("BEHAVIORAL FAIL: still using inspect.signature(cached_file) to filter kwargs")
    sys.exit(1)

# Check that the hub kwargs are explicitly listed
hub_kwargs = ["cache_dir", "force_download", "token", "revision", "local_files_only"]
source_lower = source

found_count = 0
for kw in hub_kwargs:
    if f'"{kw}"' in source or f"'{kw}'" in source:
        found_count += 1

if found_count >= 4:
    print(f"BEHAVIORAL PASS: {found_count}/{len(hub_kwargs)} hub kwargs explicitly listed (no longer using inspect.signature)")
    sys.exit(0)
else:
    print(f"BEHAVIORAL FAIL: only {found_count}/{len(hub_kwargs)} hub kwargs found as explicit strings")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Regression - cached_file_kwargs dict is still built ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()

# Check that cached_file_kwargs is still constructed and used
if "cached_file_kwargs" not in source:
    print("REGRESSION FAIL: cached_file_kwargs no longer present")
    sys.exit(1)

# Check that cached_file is still called
if "cached_file(" not in source:
    print("REGRESSION FAIL: cached_file() call not found")
    sys.exit(1)

print("REGRESSION PASS: cached_file_kwargs and cached_file() call still present")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - inspect import removed ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that 'import inspect' is no longer present
has_inspect_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "inspect":
                has_inspect_import = True
    elif isinstance(node, ast.ImportFrom):
        if node.module == "inspect":
            has_inspect_import = True

if has_inspect_import:
    # Check if inspect is used anywhere else in the file (it might be needed elsewhere)
    # Count usages of inspect. beyond the import
    if source.count("inspect.") > 0:
        print("STRUCTURAL PASS: inspect still imported and used elsewhere")
        sys.exit(0)
    else:
        print("STRUCTURAL FAIL: inspect imported but no longer used")
        sys.exit(1)
else:
    print("STRUCTURAL PASS: unused inspect import removed")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/models/auto/processing_auto.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class AutoProcessor" in source, "AutoProcessor class present"),
    ("from_pretrained" in source, "from_pretrained method present"),
    ("cached_file" in source, "cached_file referenced"),
    (len(source.splitlines()) > 100, "file has substantial content"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi


# ---------- CONFIG-DERIVED (5%): ruff format check on changed files ----------
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit c17877c2ad39f8f736d5ea8a34f98e562843fc83
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/models/auto/processing_auto.py; do
    if [ -f "$f" ]; then
        ruff check --select I "$f" 2>/dev/null
        if [ $? -ne 0 ]; then RUFF_OK=false; fi
    fi
done
if [ "$RUFF_OK" = true ]; then
    RESULTS[config_ruff]=1
    echo "TEST config_ruff: PASS"
else
    echo "TEST config_ruff: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  regression (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  structural (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff    (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
