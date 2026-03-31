#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_core]=0.40
WEIGHTS[behavioral_integration]=0.25
WEIGHTS[regression]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_ruff_format]=0.05

for key in behavioral_core behavioral_integration regression antistub config_ruff_format; do
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

# ---------- PRIMARY BEHAVIORAL (40%): Config is actually regenerated and assigned ----------
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find SpacesReloader class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL_CORE FAIL: SpacesReloader class not found")
    sys.exit(1)

# Extract the full class source for analysis
lines = source.splitlines()
cls_src = "\n".join(lines[cls_node.lineno - 1 : cls_node.end_lineno])

# Check that get_config_file is called and its result assigned to demo.config
# Look for pattern: demo.config = ...get_config_file(...) or similar
has_config_assignment = False

# Parse the class body for config assignment
for node in ast.walk(cls_node):
    # Look for assignment to demo.config or similar
    if isinstance(node, ast.Assign):
        for target in node.targets:
            # Check for attribute assignment like x.config = ...
            if isinstance(target, ast.Attribute) and target.attr == "config":
                # Check if value involves get_config_file call
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "get_config_file":
                        has_config_assignment = True
                        break
                    # Also check for demo.get_config_file() pattern
                    if isinstance(node.value.func, ast.Name) and node.value.func.id == "get_config_file":
                        has_config_assignment = True
                        break
    # Also check for augmented assignment
    elif isinstance(node, ast.AugAssign):
        if isinstance(node.target, ast.Attribute) and node.target.attr == "config":
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "get_config_file":
                    has_config_assignment = True
                    break

if has_config_assignment:
    print("BEHAVIORAL_CORE PASS: demo.config is assigned from get_config_file()")
    sys.exit(0)

# Alternative: Check if swap_blocks or postrun contains the call pattern via source analysis
# This catches edge cases the AST might miss
if "demo.config = demo.get_config_file()" in cls_src or ".config = " in cls_src:
    # Verify it's related to get_config_file
    if "get_config_file" in cls_src:
        print("BEHAVIORAL_CORE PASS: config assignment pattern found")
        sys.exit(0)

print("BEHAVIORAL_CORE FAIL: demo.config is not reassigned from get_config_file()")
print("The fix requires: demo.config = demo.get_config_file()")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_core]=1
    echo "TEST behavioral_core: PASS"
else
    echo "TEST behavioral_core: FAIL"
fi

# ---------- SECONDARY BEHAVIORAL (25%): swap_blocks override exists and calls parent ----------
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find SpacesReloader class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL_INTEGRATION FAIL: SpacesReloader class not found")
    sys.exit(1)

# Find swap_blocks method
swap_blocks_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "swap_blocks":
        swap_blocks_node = item
        break

if swap_blocks_node is None:
    print("BEHAVIORAL_INTEGRATION FAIL: SpacesReloader.swap_blocks override not found")
    sys.exit(1)

# Check that it calls the parent method (super().swap_blocks())
has_super_call = False
for node in ast.walk(swap_blocks_node):
    if isinstance(node, ast.Call):
        # Check for super().swap_blocks(...) or super(SpacesReloader, self).swap_blocks(...)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "swap_blocks":
            if isinstance(node.func.value, ast.Call):
                # super() call
                if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                    has_super_call = True
                    break
            elif isinstance(node.func.value, ast.Name) and node.func.value.id == "super":
                has_super_call = True
                break

if has_super_call:
    print("BEHAVIORAL_INTEGRATION PASS: swap_blocks calls parent implementation")
    sys.exit(0)
else:
    print("BEHAVIORAL_INTEGRATION FAIL: swap_blocks does not call parent super().swap_blocks()")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_integration]=1
    echo "TEST behavioral_integration: PASS"
else
    echo "TEST behavioral_integration: FAIL"
fi

# ---------- REGRESSION (15%): postrun still works correctly ----------
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("REGRESSION FAIL: SpacesReloader class not found")
    sys.exit(1)

# Find postrun method
postrun_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "postrun":
        postrun_node = item
        break

if postrun_node is None:
    print("REGRESSION FAIL: postrun method not found")
    sys.exit(1)

# Check postrun still calls swap_blocks (the logic flow is preserved)
postrun_src = ast.get_source_segment(source, postrun_node)
if postrun_src is None:
    lines = source.splitlines()
    postrun_src = "\n".join(lines[postrun_node.lineno - 1 : postrun_node.end_lineno])

# The postrun should call swap_blocks (either directly or through inheritance)
# In the buggy code, postrun calls self.swap_blocks()
# In the fixed code, either:
#   1. postrun still calls self.swap_blocks() which now hits the override, OR
#   2. The logic is preserved in some other way

# Check for swap_blocks call
has_swap_call = False
for node in ast.walk(postrun_node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "swap_blocks":
            has_swap_call = True
            break
        if isinstance(node.func, ast.Name) and node.func.id == "swap_blocks":
            has_swap_call = True
            break

if has_swap_call:
    print("REGRESSION PASS: postrun still calls swap_blocks")
    sys.exit(0)

# Alternative: If swap_blocks is overridden, the direct call might have been removed
# but the override handles it. Check that postrun logic flow is preserved.
# At minimum, postrun should still check if demo changed
if "is not self.running_app.blocks" in postrun_src:
    print("REGRESSION PASS: postrun logic flow preserved")
    sys.exit(0)

print("REGRESSION FAIL: postrun logic may be broken")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- Anti-stub check (15%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

# Check SpacesReloader class exists and has substantial implementation
checks = [
    ("class SpacesReloader" in source, "SpacesReloader class present"),
    ("def postrun" in source, "postrun method present"),
    ("def swap_blocks" in source, "swap_blocks method present"),
    ("demo.config" in source, "config assignment present"),
    ("get_config_file" in source, "get_config_file referenced"),
    (len(source.splitlines()) > 100, "file has substantial content"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file has expected implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Config-derived test (5%): "Python code formatted with ruff" ----------
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
weights = {'behavioral_core': ${WEIGHTS[behavioral_core]}, 'behavioral_integration': ${WEIGHTS[behavioral_integration]}, 'regression': ${WEIGHTS[regression]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff_format': ${WEIGHTS[config_ruff_format]}}
results = {'behavioral_core': ${RESULTS[behavioral_core]}, 'behavioral_integration': ${RESULTS[behavioral_integration]}, 'regression': ${RESULTS[regression]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff_format': ${RESULTS[config_ruff_format]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_core (${WEIGHTS[behavioral_core]}): ${RESULTS[behavioral_core]}"
echo "  behavioral_integration (${WEIGHTS[behavioral_integration]}): ${RESULTS[behavioral_integration]}"
echo "  regression (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff_format (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
