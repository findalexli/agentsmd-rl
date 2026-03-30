#!/usr/bin/env bash
#
# Verification for slime-moe-dispatcher-type-propagate
# Tests that moe_token_dispatcher_type is propagated from args to provider in bridge mode.
#
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/model_provider.py"
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

# ---------- PRIMARY 1 (35%): Behavioral - moe_token_dispatcher_type is propagated ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the wrapped_model_provider function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "wrapped_model_provider":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: wrapped_model_provider function not found")
    sys.exit(1)

# Look for assignment: provider.moe_token_dispatcher_type = args.moe_token_dispatcher_type
found_propagation = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Attribute) and
                target.attr == "moe_token_dispatcher_type" and
                isinstance(target.value, ast.Name) and
                target.value.id == "provider"):
                found_propagation = True
                break
    if found_propagation:
        break

if found_propagation:
    print("BEHAVIORAL PASS: moe_token_dispatcher_type is propagated to provider")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: moe_token_dispatcher_type not propagated to provider")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (35%): Behavioral - propagation is guarded by hasattr/getattr ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "wrapped_model_provider":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL2 FAIL: function not found")
    sys.exit(1)

# Find the assignment to provider.moe_token_dispatcher_type
# It should be inside an if-block that checks hasattr or getattr for "moe_token_dispatcher_type"
# Walk all If nodes and check if they contain the assignment AND have a guard
found_guarded = False
for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        # Check if the test is a hasattr/getattr call with "moe_token_dispatcher_type"
        has_guard = False
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Call):
                fn = sub.func
                if isinstance(fn, ast.Name) and fn.id in ("hasattr", "getattr"):
                    for arg in sub.args:
                        if isinstance(arg, ast.Constant) and arg.value == "moe_token_dispatcher_type":
                            has_guard = True
                            break
            if has_guard:
                break

        if has_guard:
            # Check if body contains assignment to provider.moe_token_dispatcher_type
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign):
                    for t in sub.targets:
                        if (isinstance(t, ast.Attribute) and t.attr == "moe_token_dispatcher_type"):
                            found_guarded = True
                            break
                if found_guarded:
                    break
    if found_guarded:
        break

if found_guarded:
    print("BEHAVIORAL2 PASS: moe_token_dispatcher_type propagation is guarded by hasattr/getattr")
    sys.exit(0)
else:
    # Also accept getattr with default pattern (no if-block needed)
    found_getattr = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (isinstance(t, ast.Attribute) and t.attr == "moe_token_dispatcher_type" and
                    isinstance(t.value, ast.Name) and t.value.id == "provider"):
                    # Check if value uses getattr
                    if isinstance(node.value, ast.Call):
                        fn = node.value.func
                        if isinstance(fn, ast.Name) and fn.id == "getattr":
                            found_getattr = True
            if found_getattr:
                break

    if found_getattr:
        print("BEHAVIORAL2 PASS: moe_token_dispatcher_type uses getattr with default")
        sys.exit(0)
    else:
        print("BEHAVIORAL2 FAIL: propagation not guarded by hasattr/getattr")
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- SECONDARY (30%): Structural - placement near other provider assignments ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "wrapped_model_provider":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: function not found")
    sys.exit(1)

# Check that there's an assignment to provider.variable_seq_lengths
# AND provider.moe_token_dispatcher_type, meaning the new assignment
# is placed in the same region as other provider configuration
has_variable_seq = False
has_moe_dispatcher = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "provider":
                if t.attr == "variable_seq_lengths":
                    has_variable_seq = True
                if t.attr == "moe_token_dispatcher_type":
                    has_moe_dispatcher = True

if has_variable_seq and has_moe_dispatcher:
    print("STRUCTURAL PASS: both variable_seq_lengths and moe_token_dispatcher_type are set on provider")
    sys.exit(0)
else:
    print(f"STRUCTURAL FAIL: variable_seq_lengths={has_variable_seq}, moe_token_dispatcher_type={has_moe_dispatcher}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 7f2a03b5d390f93a90776b8d99ace6b82fa61738
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 7f2a03b5d390f93a90776b8d99ace6b82fa61738
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
