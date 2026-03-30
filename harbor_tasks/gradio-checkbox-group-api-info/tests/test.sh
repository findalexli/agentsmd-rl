#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15

WEIGHTS[config_ruff_format]=0.05

for key in behavioral regression structural antistub config_ruff_format; do
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

# ---------- PRIMARY 1 (35%): Behavioral - api_info() does not raise AttributeError ----------
python3 << 'PYEOF'
import ast, sys, textwrap

TARGET = "/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the ColoredCheckboxGroup class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ColoredCheckboxGroup":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL FAIL: ColoredCheckboxGroup class not found")
    sys.exit(1)

# Find the api_info method
api_info_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info_node = item
        break

if api_info_node is None:
    print("BEHAVIORAL FAIL: api_info method not found")
    sys.exit(1)

# Create a mock object that mimics ColoredCheckboxGroup with props dict
# but WITHOUT self.choices (which is the bug trigger)
class MockColoredCheckboxGroup:
    def __init__(self):
        self.props = {"choices": ["red", "green", "blue"]}

mock_obj = MockColoredCheckboxGroup()

# Extract and exec the api_info method
api_info_source = ast.get_source_segment(source, api_info_node)
if api_info_source is None:
    lines = source.splitlines()
    api_info_source = "\n".join(lines[api_info_node.lineno - 1 : api_info_node.end_lineno])

api_info_source = textwrap.dedent(api_info_source)
exec_globals = {}
exec(compile(api_info_source, "<api_info>", "exec"), exec_globals)
api_info_func = exec_globals.get("api_info")

if api_info_func is None:
    print("BEHAVIORAL FAIL: could not compile api_info function")
    sys.exit(1)

try:
    result = api_info_func(mock_obj)
    if not isinstance(result, dict):
        print(f"BEHAVIORAL FAIL: api_info returned {type(result)}, expected dict")
        sys.exit(1)
    if "items" not in result:
        print("BEHAVIORAL FAIL: result missing 'items' key")
        sys.exit(1)
    if result["items"].get("enum") != ["red", "green", "blue"]:
        print(f"BEHAVIORAL FAIL: items.enum = {result['items'].get('enum')}, expected ['red', 'green', 'blue']")
        sys.exit(1)
    print("BEHAVIORAL PASS: api_info() returns correct schema without AttributeError")
except AttributeError as e:
    print(f"BEHAVIORAL FAIL: AttributeError raised: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Regression - api_info returns proper schema structure ----------
python3 << 'PYEOF'
import ast, sys, textwrap

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
    print("REGRESSION FAIL: class not found")
    sys.exit(1)

api_info_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info_node = item
        break

if api_info_node is None:
    print("REGRESSION FAIL: api_info not found")
    sys.exit(1)

api_info_source = ast.get_source_segment(source, api_info_node)
if api_info_source is None:
    lines = source.splitlines()
    api_info_source = "\n".join(lines[api_info_node.lineno - 1 : api_info_node.end_lineno])

api_info_source = textwrap.dedent(api_info_source)
exec_globals = {}
exec(compile(api_info_source, "<api_info>", "exec"), exec_globals)
api_info_func = exec_globals.get("api_info")

class MockBoth:
    def __init__(self):
        self.props = {"choices": ["a", "b", "c"]}
        self.choices = ["a", "b", "c"]

mock = MockBoth()
try:
    result = api_info_func(mock)
    assert result["title"] == "Checkbox Group", f"title mismatch: {result.get('title')}"
    assert result["type"] == "array", f"type mismatch: {result.get('type')}"
    assert result["items"]["type"] == "string", f"items.type mismatch"
    print("REGRESSION PASS: schema structure is correct")
except Exception as e:
    print(f"REGRESSION FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - uses self.props["choices"] not self.choices ----------
python3 << 'PYEOF'
import ast, sys, re

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
    print("STRUCTURAL FAIL: class not found")
    sys.exit(1)

api_info_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "api_info":
        api_info_node = item
        break

if api_info_node is None:
    print("STRUCTURAL FAIL: api_info not found")
    sys.exit(1)

api_info_src = ast.get_source_segment(source, api_info_node)
if api_info_src is None:
    lines = source.splitlines()
    api_info_src = "\n".join(lines[api_info_node.lineno - 1 : api_info_node.end_lineno])

# The buggy pattern is: self.choices (bare, not via self.props)
# Check for self.props["choices"] or self.props['choices']
has_props_choices = bool(re.search(r'self\.props\[.choices.\]', api_info_src))
has_bare_choices = bool(re.search(r'self\.choices\b', api_info_src))

if has_props_choices:
    print("STRUCTURAL PASS: uses self.props['choices']")
    sys.exit(0)
elif not has_bare_choices:
    # Some other valid approach
    print("STRUCTURAL PASS: does not use bare self.choices")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: still using bare self.choices")
    sys.exit(1)
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

TARGET = "/workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class ColoredCheckboxGroup" in source, "class definition present"),
    ("def api_info" in source, "api_info method present"),
    ("def __init__" in source, "__init__ method present"),
    (len(source.splitlines()) > 20, "file has substantial content"),
    (len(source) > 500, "file has substantial size"),
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
# Source: AGENTS.md line 43 @ commit ebbd24231dbc006c21fbbf1df00918be16883b86
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/components/custom_html_components/colored_checkbox_group.py 2>/dev/null
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
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff_format': ${WEIGHTS[config_ruff_format]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff_format': ${RESULTS[config_ruff_format]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  regression (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  structural (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff_format (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
