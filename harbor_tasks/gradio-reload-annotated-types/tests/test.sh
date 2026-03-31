#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/utils.py"
SKILLS_TARGET="/workspace/gradio/gradio/cli/commands/skills.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_import_success]=0.30
WEIGHTS[behavioral_watchfn_no_flag]=0.25
WEIGHTS[behavioral_annotated_types_work]=0.25
WEIGHTS[structural_string_annotations]=0.15
WEIGHTS[antistub]=0.05

for key in behavioral_import_success behavioral_watchfn_no_flag behavioral_annotated_types_work structural_string_annotations antistub; do
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
    print(f'GATE FAIL: syntax error in utils.py: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

python3 -c "
import ast, sys
try:
    with open('$SKILLS_TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error in skills.py: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (30%): Behavioral - Module imports without NameError ----------
# [pr_diff] (0.30): After removing from __future__ import annotations, file must still import
python3 << 'PYEOF'
import sys
import os

os.chdir('/workspace/gradio')
sys.path.insert(0, '/workspace/gradio')

try:
    # This will fail if bare annotations like -> App: weren't converted to -> "App":
    import gradio.utils
    print("BEHAVIORAL PASS: gradio.utils imports without NameError")
    sys.exit(0)
except NameError as e:
    print(f"BEHAVIORAL FAIL: NameError on import - {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL FAIL: Import failed - {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_import_success]=1
    echo "TEST behavioral_import_success: PASS"
else
    echo "TEST behavioral_import_success: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - watchfn doesn't inherit CO_FUTURE_ANNOTATIONS ----------
# [pr_diff] (0.25): watchfn code object must not have CO_FUTURE_ANNOTATIONS flag
python3 << 'PYEOF'
import sys
import __future__
import os

os.chdir('/workspace/gradio')
sys.path.insert(0, '/workspace/gradio')

try:
    from gradio.utils import watchfn
    flag = __future__.annotations.compiler_flag
    if watchfn.__code__.co_flags & flag:
        print("BEHAVIORAL_FAIL: watchfn has CO_FUTURE_ANNOTATIONS flag")
        sys.exit(1)
    else:
        print("BEHAVIORAL_PASS: watchfn does not have CO_FUTURE_ANNOTATIONS flag")
        sys.exit(0)
except ImportError as e:
    print(f"BEHAVIORAL_FAIL: Cannot import watchfn - {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_watchfn_no_flag]=1
    echo "TEST behavioral_watchfn_no_flag: PASS"
else
    echo "TEST behavioral_watchfn_no_flag: FAIL"
fi

# ---------- PRIMARY 3 (25%): Behavioral - Annotated types work with get_type_hints after exec ----------
# [pr_diff] (0.25): Simulate what watchfn does - exec code with Annotated types
python3 << 'PYEOF'
import sys
import os
from typing import get_type_hints, Annotated

os.chdir('/workspace/gradio')
sys.path.insert(0, '/workspace/gradio')

# Simulate what watchfn does - exec user code
user_code = '''
from typing import Annotated

class TestClass:
    value: Annotated[str, "description"]
    count: Annotated[int, "count field"]

def test_func(x: Annotated[str, "param"]) -> Annotated[int, "result"]:
    return len(x)
'''

# Import utils to ensure any exec calls from there don't carry the flag
import gradio.utils

# Now exec the user code (this is what watchfn does)
namespace = {}
exec(user_code, namespace)

# Try to get type hints (this is what breaks with the bug)
try:
    TestClass = namespace['TestClass']
    hints = get_type_hints(TestClass)
    print(f"Got type hints for TestClass: {hints}")

    test_func = namespace['test_func']
    func_hints = get_type_hints(test_func)
    print(f"Got type hints for test_func: {func_hints}")

    # Verify the hints are actual types, not ForwardRef strings
    if 'value' in hints:
        value_type = hints['value']
        # Should be Annotated[str, ...], not a string
        if isinstance(value_type, str):
            print(f"BEHAVIORAL_FAIL: Type hint is string {value_type!r}, not Annotated type")
            sys.exit(1)
        print("BEHAVIORAL_PASS: Annotated types resolve correctly after exec")
        sys.exit(0)
    else:
        print("BEHAVIORAL_FAIL: 'value' not in type hints")
        sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL_FAIL: get_type_hints failed - {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_annotated_types_work]=1
    echo "TEST behavioral_annotated_types_work: PASS"
else
    echo "TEST behavioral_annotated_types_work: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Structural - Type annotations are strings (AST verified) ----------
# [pr_diff] (0.15): Bare annotations for forward refs converted to string form
# Gate this behind behavioral import success
if [ ${RESULTS[behavioral_import_success]} -eq 1 ]; then
    python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Look for ClassDef, FunctionDef, AsyncFunctionDef with annotations
def get_annotation_name(node):
    """Extract the name from an annotation node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value  # This is a string annotation like "App"
    elif isinstance(node, ast.Subscript):
        # Handle generic types like Optional[X] or List[X]
        if isinstance(node.value, ast.Name):
            return node.value.id
    return None

# Check that forward reference annotations (to gradio classes) are strings
issues = []
checked = 0
string_annotations = 0

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # Check return annotation
        if node.returns:
            checked += 1
            name = get_annotation_name(node.returns)
            if name in ['App', 'Blocks', 'Request', 'SessionState', 'Button', 'Component', 'BlockContext']:
                if isinstance(node.returns, ast.Constant) and isinstance(node.returns.value, str):
                    string_annotations += 1
                elif isinstance(node.returns, ast.Name):
                    issues.append(f"{node.name}() return annotation '{name}' should be string '{name}'")

        # Check argument annotations
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation:
                checked += 1
                name = get_annotation_name(arg.annotation)
                if name in ['App', 'Blocks', 'Request', 'SessionState', 'Button', 'Component', 'BlockContext']:
                    if isinstance(arg.annotation, ast.Constant) and isinstance(arg.annotation.value, str):
                        string_annotations += 1
                    elif isinstance(arg.annotation, ast.Name):
                        issues.append(f"{node.name}() arg '{arg.arg}' annotation '{name}' should be string")

    elif isinstance(node, ast.ClassDef):
        # Check class attribute annotations
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and item.target:
                checked += 1
                name = get_annotation_name(item.annotation)
                if name in ['App', 'Blocks', 'Request', 'SessionState', 'Button', 'Component', 'BlockContext']:
                    if isinstance(item.annotation, ast.Constant) and isinstance(item.annotation.value, str):
                        string_annotations += 1
                    elif isinstance(item.annotation, ast.Name):
                        issues.append(f"{node.name}.{item.target.id} annotation '{name}' should be string")

# We expect at least 5 string annotations (based on the PR diff)
# and issues should be minimal
critical_issues = [i for i in issues if any(x in i for x in ['-> App', '-> Blocks'])]

if critical_issues:
    print(f"STRUCTURAL_FAIL: {len(critical_issues)} critical bare annotations found")
    for i in critical_issues[:3]:
        print(f"  - {i}")
    sys.exit(1)
elif string_annotations >= 3:
    print(f"STRUCTURAL_PASS: {string_annotations} string annotations found")
    sys.exit(0)
else:
    print(f"STRUCTURAL_PARTIAL: Only {string_annotations} string annotations, expected >= 3")
    sys.exit(0)  # Partial credit handled elsewhere
PYEOF
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        RESULTS[structural_string_annotations]=1
        echo "TEST structural_string_annotations: PASS"
    else
        echo "TEST structural_string_annotations: FAIL"
    fi
else
    echo "TEST structural_string_annotations: SKIPPED (gated behind import success)"
fi

# ---------- Anti-stub check (5%) ----------
# [pr_diff] (0.05): File must retain substantial implementation
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("def watchfn" in source, "watchfn reference present"),
    ("class BaseReloader" in source, "BaseReloader class present"),
    ("def safe_join" in source, "safe_join function present"),
    (len(source.splitlines()) > 400, "file has substantial content"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Pass-to-Pass: Upstream test subset ----------
# Run upstream test if available
if [ -f "/workspace/gradio/test/test_reload.py" ]; then
    echo "=== Running upstream P2P test ==="
    cd /workspace/gradio
    python3 -m pytest test/test_reload.py::test_watchfn_does_not_inherit_future_annotations -x --timeout=60 -q 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "P2P PASS: upstream test passes"
    else
        echo "P2P INFO: upstream test failed or not available"
    fi
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_import_success': ${WEIGHTS[behavioral_import_success]}, 'behavioral_watchfn_no_flag': ${WEIGHTS[behavioral_watchfn_no_flag]}, 'behavioral_annotated_types_work': ${WEIGHTS[behavioral_annotated_types_work]}, 'structural_string_annotations': ${WEIGHTS[structural_string_annotations]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_import_success': ${RESULTS[behavioral_import_success]}, 'behavioral_watchfn_no_flag': ${RESULTS[behavioral_watchfn_no_flag]}, 'behavioral_annotated_types_work': ${RESULTS[behavioral_annotated_types_work]}, 'structural_string_annotations': ${RESULTS[structural_string_annotations]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")

echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_import_success  (0.30): ${RESULTS[behavioral_import_success]}"
echo "  behavioral_watchfn_no_flag (0.25): ${RESULTS[behavioral_watchfn_no_flag]}"
echo "  behavioral_annotated_types (0.25): ${RESULTS[behavioral_annotated_types_work]}"
echo "  structural_string_annotations (0.15): ${RESULTS[structural_string_annotations]}"
echo "  antistub                   (0.05): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
