#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_f2p]=0.45
WEIGHTS[behavioral_p2p]=0.25
WEIGHTS[antistub]=0.10

WEIGHTS[config_ruff_format]=0.05

for key in behavioral_f2p behavioral_p2p antistub config_ruff_format; do
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

# ---------- GATE: Required class and method exist ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ColoredCheckboxGroup":
        cls_node = node
        break

if cls_node is None:
    print("GATE FAIL: ColoredCheckboxGroup class not found")
    sys.exit(1)

api_info_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info_node = item
        break

if api_info_node is None:
    print("GATE FAIL: api_info method not found")
    sys.exit(1)

# Check that api_info has actual implementation (not just pass)
body = [n for n in api_info_node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant)]
if len(body) < 2:
    print("GATE FAIL: api_info appears to be a stub")
    sys.exit(1)

print("GATE PASS: class and method present with implementation")
PYEOF
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY (45%): Fail-to-pass - api_info() doesn't raise AttributeError ----------
# [pr_diff] (0.45): Fix AttributeError by using self.props["choices"] instead of self.choices
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/gradio')

TARGET = "/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"

# Read source to check for bare self.choices (the bug pattern)
with open(TARGET) as f:
    source = f.read()

# The buggy code uses self.choices - check it's NOT present in api_info
import ast
tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ColoredCheckboxGroup":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL_F2P FAIL: class not found")
    sys.exit(1)

api_info_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info_node = item
        break

if api_info_node is None:
    print("BEHAVIORAL_F2P FAIL: api_info not found")
    sys.exit(1)

# Check for bare self.choices in api_info (the bug)
for node in ast.walk(api_info_node):
    if isinstance(node, ast.Attribute):
        if node.attr == "choices":
            # Check it's self.choices, not self.props["choices"] or similar
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                print("BEHAVIORAL_F2P FAIL: api_info still uses bare self.choices (bug not fixed)")
                sys.exit(1)

try:
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    # Create instance - this is the real test
    component = ColoredCheckboxGroup(
        choices=["red", "green", "blue"],
        colors=["#FF0000", "#00FF00", "#0000FF"],
        label="Test"
    )

    # Call api_info - this should NOT raise AttributeError on fixed code
    result = component.api_info()

    # Validate return structure
    if not isinstance(result, dict):
        print(f"BEHAVIORAL_F2P FAIL: api_info returned {type(result)}, expected dict")
        sys.exit(1)

    if "items" not in result:
        print("BEHAVIORAL_F2P FAIL: result missing 'items' key")
        sys.exit(1)

    items = result["items"]
    if "enum" not in items:
        print("BEHAVIORAL_F2P FAIL: items missing 'enum' key")
        sys.exit(1)

    if items["enum"] != ["red", "green", "blue"]:
        print(f"BEHAVIORAL_F2P FAIL: enum = {items['enum']}, expected ['red', 'green', 'blue']")
        sys.exit(1)

    print("BEHAVIORAL_F2P PASS: api_info() works without AttributeError")

except AttributeError as e:
    print(f"BEHAVIORAL_F2P FAIL: AttributeError raised: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"BEHAVIORAL_F2P FAIL: Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL_F2P FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_f2p]=1
    echo "TEST behavioral_f2p: PASS"
else
    echo "TEST behavioral_f2p: FAIL"
fi

# ---------- SECONDARY (25%): Pass-to-pass - schema structure is correct ----------
# [pr_diff] (0.25): api_info returns proper API schema structure
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/gradio')

try:
    from gradio.components.custom_html_components.colored_checkbox_group import ColoredCheckboxGroup

    component = ColoredCheckboxGroup(
        choices=["a", "b"],
        colors=["#FF0000", "#00FF00"],
        label="P2P Test"
    )

    result = component.api_info()

    # Validate full schema structure
    assert result.get("title") == "Checkbox Group", f"title mismatch: {result.get('title')}"
    assert result.get("type") == "array", f"type mismatch: {result.get('type')}"

    items = result.get("items", {})
    assert items.get("type") == "string", f"items.type mismatch: {items.get('type')}"
    assert "enum" in items, "items missing enum"

    # Test with empty choices edge case
    component_empty = ColoredCheckboxGroup(
        choices=[],
        colors=[],
        label="Empty"
    )
    result_empty = component_empty.api_info()
    assert result_empty["items"]["enum"] == [], f"empty enum mismatch: {result_empty['items']['enum']}"

    print("BEHAVIORAL_P2P PASS: schema structure correct, edge cases handled")

except Exception as e:
    print(f"BEHAVIORAL_P2P FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_p2p]=1
    echo "TEST behavioral_p2p: PASS"
else
    echo "TEST behavioral_p2p: FAIL"
fi

# ---------- Anti-stub check (10%) - only counts if behavioral passes ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find ColoredCheckboxGroup class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ColoredCheckboxGroup":
        cls_node = node
        break

if cls_node is None:
    print("ANTI-STUB FAIL: class not found")
    sys.exit(1)

# Check api_info has meaningful implementation
api_info = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info = item
        break

if api_info is None:
    print("ANTI-STUB FAIL: api_info not found")
    sys.exit(1)

# Count non-docstring statements
statements = [n for n in api_info.body
              if not isinstance(n, ast.Expr) or not isinstance(n.value, (ast.Constant, ast.Str))]

if len(statements) < 3:
    print(f"ANTI-STUB FAIL: api_info has only {len(statements)} meaningful statements")
    sys.exit(1)

# Check for return statement with dict
has_return_dict = False
for node in ast.walk(api_info):
    if isinstance(node, ast.Return):
        if isinstance(node.value, ast.Dict):
            has_return_dict = True
            break

if not has_return_dict:
    print("ANTI-STUB FAIL: api_info should return a dict")
    sys.exit(1)

print("ANTI-STUB PASS: api_info has substantial implementation")
PYEOF
ANTI_STUB_EXIT=$?
if [ $ANTI_STUB_EXIT -eq 0 ]; then
    # Only award anti-stub points if behavioral tests passed
    if [ ${RESULTS[behavioral_f2p]} -eq 1 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        RESULTS[antistub]=0
        echo "TEST antistub: SKIPPED (behavioral_f2p failed)"
    fi
else
    # If anti-stub fails, zero out all behavioral scores
    echo "TEST antistub: FAIL (stub detected - zeroing behavioral scores)"
    RESULTS[behavioral_f2p]=0
    RESULTS[behavioral_p2p]=0
    RESULTS[antistub]=0
fi

# ---------- Config-derived test (5%): ruff format check ----------
# [agent_config] (0.05): "Run ruff format" - AGENTS.md:43 @ ebbd242
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I "$TARGET" 2>/dev/null
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
weights = {'behavioral_f2p': ${WEIGHTS[behavioral_f2p]}, 'behavioral_p2p': ${WEIGHTS[behavioral_p2p]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff_format': ${WEIGHTS[config_ruff_format]}}
results = {'behavioral_f2p': ${RESULTS[behavioral_f2p]}, 'behavioral_p2p': ${RESULTS[behavioral_p2p]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff_format': ${RESULTS[config_ruff_format]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_f2p (${WEIGHTS[behavioral_f2p]}): ${RESULTS[behavioral_f2p]}"
echo "  behavioral_p2p (${WEIGHTS[behavioral_p2p]}): ${RESULTS[behavioral_p2p]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff_format (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
