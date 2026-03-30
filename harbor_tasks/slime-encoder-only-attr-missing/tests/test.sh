#!/usr/bin/env bash
#
# Verification for slime-encoder-only-attr-missing
# Tests that launch_server_process handles missing encoder_only attribute.
#
set +e

TARGET="/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.30
WEIGHTS[behavioral2]=0.30
WEIGHTS[structural]=0.30
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
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

# ---------- PRIMARY 1 (35%): Behavioral - ServerArgs without encoder_only should not crash ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: launch_server_process function not found")
    sys.exit(1)

# Find the if-statement that references encoder_only
if_node = None
for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Attribute) and sub.attr == "encoder_only":
                if_node = node
                break
            if isinstance(sub, ast.Constant) and sub.value == "encoder_only":
                if_node = node
                break
        if if_node:
            break

if if_node is None:
    print("BEHAVIORAL FAIL: no if-statement referencing encoder_only found")
    sys.exit(1)

# Compile and evaluate the test expression with a mock object lacking encoder_only
class FakeArgs:
    pass

try:
    test_expr = ast.Expression(body=if_node.test)
    ast.fix_missing_locations(test_expr)
    code = compile(test_expr, "<test>", "eval")
    result = eval(code, {"server_args": FakeArgs(), "hasattr": hasattr, "getattr": getattr})
    if result:
        print("BEHAVIORAL FAIL: condition should be False when encoder_only is missing")
        sys.exit(1)
    print("BEHAVIORAL PASS: no AttributeError when encoder_only is missing")
    sys.exit(0)
except AttributeError as e:
    print(f"BEHAVIORAL FAIL: AttributeError raised: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (35%): Behavioral - ServerArgs WITH encoder_only=True should still work ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL2 FAIL: function not found")
    sys.exit(1)

# Find the if-statement with encoder_only
if_node = None
for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Attribute) and sub.attr == "encoder_only":
                if_node = node
                break
            if isinstance(sub, ast.Constant) and sub.value == "encoder_only":
                if_node = node
                break
        if if_node:
            break

if if_node is None:
    print("BEHAVIORAL2 FAIL: no if-statement referencing encoder_only found")
    sys.exit(1)

# Test with an object that HAS encoder_only=True
class FakeArgsWithEncoder:
    encoder_only = True

try:
    test_expr = ast.Expression(body=if_node.test)
    ast.fix_missing_locations(test_expr)
    code = compile(test_expr, "<test>", "eval")
    result = eval(code, {"server_args": FakeArgsWithEncoder(), "hasattr": hasattr, "getattr": getattr})
    if result:
        print("BEHAVIORAL2 PASS: condition is True when encoder_only=True")
        sys.exit(0)
    else:
        print("BEHAVIORAL2 FAIL: condition should be True when encoder_only=True")
        sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL2 FAIL: error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- SECONDARY (30%): Structural - hasattr or getattr guard present ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: function not found")
    sys.exit(1)

# Check that there's a hasattr or getattr call with "encoder_only" in the function
has_guard = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("hasattr", "getattr"):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "encoder_only":
                    has_guard = True
                    break
    if has_guard:
        break

if has_guard:
    print("STRUCTURAL PASS: hasattr/getattr guard found for encoder_only")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: no hasattr/getattr guard for encoder_only")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 6f70479966749e258ba0b20341e2c4b88ea094f1
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 6f70479966749e258ba0b20341e2c4b88ea094f1
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
