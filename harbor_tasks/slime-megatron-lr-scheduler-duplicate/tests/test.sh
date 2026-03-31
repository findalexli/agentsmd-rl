#!/usr/bin/env bash
#
# Verification for slime-megatron-lr-scheduler-duplicate
# Tests that the redundant opt_param_scheduler.step() call has been removed
# from initialize_model_and_optimizer().
#
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/model.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.60
WEIGHTS[regression]=0.15
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral regression config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
# [agent_config] (gate): Syntax gate - invalid code scores 0
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

# ---------- PRIMARY (60%): Behavioral - opt_param_scheduler.step() must be removed ----------
# [pr_diff] (0.60): Remove redundant opt_param_scheduler.step() call
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model.py"

def find_function_node(tree, func_name):
    """Find a function definition by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node
    return None

def has_scheduler_step_call(func_node):
    """Check if function contains opt_param_scheduler.step() call."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "step":
                if isinstance(func.value, ast.Name) and func.value.id == "opt_param_scheduler":
                    return True
                # Also check for other scheduler variable names
                if isinstance(func.value, ast.Name):
                    scheduler_names = ["opt_param_scheduler", "scheduler", "param_scheduler", "lr_scheduler"]
                    if func.value.id in scheduler_names:
                        # Verify this is inside initialize_model_and_optimizer, not a nested call
                        return True
    return False

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the initialize_model_and_optimizer function
func_node = find_function_node(tree, "initialize_model_and_optimizer")

if func_node is None:
    print("BEHAVIORAL FAIL: initialize_model_and_optimizer function not found")
    sys.exit(1)

# Check if any call to scheduler.step() exists in the function body
if has_scheduler_step_call(func_node):
    print("BEHAVIORAL FAIL: opt_param_scheduler.step() still present in initialize_model_and_optimizer")
    sys.exit(1)

print("BEHAVIORAL PASS: opt_param_scheduler.step() removed from initialize_model_and_optimizer")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- REGRESSION (15%): Verify function still has expected structure ----------
# [pr_diff] (0.15): Function should still call setup_model_and_optimizer and load_checkpoint
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model.py"

def find_function_node(tree, func_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node
    return None

def has_call(func_node, call_name):
    """Check if function contains a call to a specific function name."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == call_name:
                return True
            if isinstance(func, ast.Attribute) and func.attr == call_name:
                return True
    return False

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)
func_node = find_function_node(tree, "initialize_model_and_optimizer")

if func_node is None:
    print("REGRESSION FAIL: function not found")
    sys.exit(1)

# Verify the function still calls essential functions
has_setup = has_call(func_node, "setup_model_and_optimizer")
has_load = has_call(func_node, "load_checkpoint")
has_return = any(isinstance(node, ast.Return) for node in ast.walk(func_node))

if not has_setup:
    print("REGRESSION FAIL: setup_model_and_optimizer call missing")
    sys.exit(1)

if not has_load:
    print("REGRESSION FAIL: load_checkpoint call missing")
    sys.exit(1)

if not has_return:
    print("REGRESSION FAIL: no return statement")
    sys.exit(1)

print("REGRESSION PASS: function structure intact")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[regression]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# [agent_config] (0.05): "Avoid wildcard imports" - .claude/skills/add-tests-and-ci/SKILL.md
# Strip comments before checking
echo "=== Config: no wildcard imports ==="
python3 -c "
import re
with open('$TARGET') as f:
    content = f.read()
# Remove comments
content = re.sub(r'#.*', '', content)
if re.search(r'from\s+\S+\s+import\s+\*', content):
    print('TEST config_no_wildcard: FAIL: wildcard import found')
    exit(1)
print('TEST config_no_wildcard: PASS')
exit(0)
"
if [ $? -eq 0 ]; then RESULTS[config_no_wildcard]=1; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# [agent_config] (0.05): "Prefer logging over print" - .claude/skills/add-tests-and-ci/SKILL.md
# Strip comments before checking
echo "=== Config: no bare print() ==="
python3 -c "
import re
with open('$TARGET') as f:
    content = f.read()
# Remove comments
content = re.sub(r'#.*', '', content)
# Check for bare print(
if re.search(r'^\s*print\(', content, re.MULTILINE):
    print('TEST config_no_bare_print: FAIL: bare print() found')
    exit(1)
print('TEST config_no_bare_print: PASS')
exit(0)
"
if [ $? -eq 0 ]; then RESULTS[config_no_bare_print]=1; fi

# ---------- SCORE ----------
SCORE="0"
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral regression config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
