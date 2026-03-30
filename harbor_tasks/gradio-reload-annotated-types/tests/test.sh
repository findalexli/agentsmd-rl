#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_no_future_annotations]=0.35
WEIGHTS[behavioral_watchfn_flag]=0.25
WEIGHTS[structural_string_annotations]=0.20
WEIGHTS[antistub]=0.15

WEIGHTS[config_ruff_format]=0.05

for key in behavioral_no_future_annotations behavioral_watchfn_flag structural_string_annotations antistub config_ruff_format; do
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

# ---------- PRIMARY 1 (35%): Behavioral - No from __future__ import annotations ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    content = f.read()

if "from __future__ import annotations" in content:
    print("BEHAVIORAL FAIL: 'from __future__ import annotations' still present in utils.py")
    sys.exit(1)
else:
    print("BEHAVIORAL PASS: 'from __future__ import annotations' removed from utils.py")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_no_future_annotations]=1
    echo "TEST behavioral_no_future_annotations: PASS"
else
    echo "TEST behavioral_no_future_annotations: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - watchfn does not carry CO_FUTURE_ANNOTATIONS ----------
python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check if the module has CO_FUTURE_ANNOTATIONS set
# We can verify by checking if 'from __future__ import annotations' appears as an import
has_future = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == "__future__":
        for alias in node.names:
            if alias.name == "annotations":
                has_future = True
                break

if has_future:
    print("BEHAVIORAL_WATCHFN FAIL: module still imports __future__.annotations")
    sys.exit(1)

# Also verify by compiling and checking the code object flag
import __future__
code = compile(source, TARGET, "exec")
flag = __future__.annotations.compiler_flag
if code.co_flags & flag:
    print("BEHAVIORAL_WATCHFN FAIL: compiled code has CO_FUTURE_ANNOTATIONS set")
    sys.exit(1)
else:
    print("BEHAVIORAL_WATCHFN PASS: compiled code does NOT have CO_FUTURE_ANNOTATIONS")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_watchfn_flag]=1
    echo "TEST behavioral_watchfn_flag: PASS"
else
    echo "TEST behavioral_watchfn_flag: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - Type annotations converted to strings ----------
python3 << 'PYEOF'
import sys, re

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    content = f.read()

# After removing from __future__ import annotations, bare type annotations
# like -> App, -> Blocks need to be converted to -> "App", -> "Blocks"
# Check that key function signatures use string annotations

# Check for string-form annotations for common types
string_annotations = [
    '"App"',
    '"Blocks"',
]

found = 0
for ann in string_annotations:
    if ann in content:
        found += 1

if found >= 2:
    print(f"STRUCTURAL PASS: {found}/{len(string_annotations)} type annotations converted to strings")
    sys.exit(0)
elif found >= 1:
    print(f"STRUCTURAL PARTIAL: {found}/{len(string_annotations)} type annotations converted")
    sys.exit(0)
else:
    # Maybe they used a different approach - check if the file parses without errors
    # and doesn't have bare App/Blocks in annotations that would fail
    print("STRUCTURAL FAIL: type annotations not converted to strings")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_string_annotations]=1
    echo "TEST structural_string_annotations: PASS"
else
    echo "TEST structural_string_annotations: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("def watchfn" in source or "watchfn" in source, "watchfn reference present"),
    ("class BaseReloader" in source, "BaseReloader class present"),
    ("def safe_join" in source, "safe_join function present"),
    (len(source.splitlines()) > 500, "file has substantial content"),
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


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit c4986883b267570d76b442899c6fc09d14e3e222
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/utils.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then
    RESULTS[config_ruff_format]=1
    echo "TEST config_ruff_format: PASS"
else
    echo "TEST config_ruff_format: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_no_future_annotations': ${WEIGHTS[behavioral_no_future_annotations]}, 'behavioral_watchfn_flag': ${WEIGHTS[behavioral_watchfn_flag]}, 'structural_string_annotations': ${WEIGHTS[structural_string_annotations]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff_format': ${WEIGHTS[config_ruff_format]}}
results = {'behavioral_no_future_annotations': ${RESULTS[behavioral_no_future_annotations]}, 'behavioral_watchfn_flag': ${RESULTS[behavioral_watchfn_flag]}, 'structural_string_annotations': ${RESULTS[structural_string_annotations]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff_format': ${RESULTS[config_ruff_format]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_no_future_annotations (${WEIGHTS[behavioral_no_future_annotations]}): ${RESULTS[behavioral_no_future_annotations]}"
echo "  behavioral_watchfn_flag          (${WEIGHTS[behavioral_watchfn_flag]}): ${RESULTS[behavioral_watchfn_flag]}"
echo "  structural_string_annotations    (${WEIGHTS[structural_string_annotations]}): ${RESULTS[structural_string_annotations]}"
echo "  antistub                         (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff_format               (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  config_ruff_format (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
