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
WEIGHTS[behavioral]=0.50
WEIGHTS[regression]=0.15
WEIGHTS[structural]=0.30
WEIGHTS[config_no_wildcard]=0.03
WEIGHTS[config_no_bare_print]=0.02

for key in behavioral regression structural config_no_wildcard config_no_bare_print; do
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

# ---------- BEHAVIORAL (50%): Verify moe_token_dispatcher_type propagation logic ----------
# [pr_diff] Tests that the fix actually addresses the bug
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"

def find_function(tree, name):
    """Find a function by name, including nested functions."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None

def get_all_nodes(func_node):
    """Get all nodes within a function body recursively."""
    all_nodes = []
    for child in ast.walk(func_node):
        all_nodes.append(child)
    return all_nodes

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find wrapped_model_provider function (it's nested inside get_model_provider_func)
func_node = find_function(tree, "wrapped_model_provider")

if func_node is None:
    print("BEHAVIORAL FAIL: wrapped_model_provider function not found")
    sys.exit(1)

# Check for any valid moe_token_dispatcher_type handling
# Accept multiple patterns: direct assignment, hasattr, getattr, setattr, EAFP
def check_moe_handling(func_node):
    """Check if there's valid MoE propagation logic in the function."""
    nodes = get_all_nodes(func_node)

    # Pattern 1: Direct attribute assignment: provider.moe_token_dispatcher_type = ...
    for node in nodes:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Attribute) and
                    target.attr == "moe_token_dispatcher_type" and
                    isinstance(target.value, ast.Name) and
                    target.value.id == "provider"):
                    return True, "direct_assignment"

    # Pattern 2: setattr(provider, "moe_token_dispatcher_type", ...)
    for node in nodes:
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Name) and node.func.id == "setattr"):
                if len(node.args) >= 2:
                    first_arg = node.args[0]
                    second_arg = node.args[1]
                    if (isinstance(first_arg, ast.Name) and first_arg.id == "provider" and
                        isinstance(second_arg, ast.Constant) and
                        second_arg.value == "moe_token_dispatcher_type"):
                        return True, "setattr"

    # Pattern 3: hasattr or getattr check for the attribute
    for node in nodes:
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("hasattr", "getattr"):
                    for arg in node.args:
                        if (isinstance(arg, ast.Constant) and
                            arg.value == "moe_token_dispatcher_type"):
                            return True, f"{node.func.id}_check"

    # Pattern 4: EAFP pattern - try block attempting the assignment
    for node in nodes:
        if isinstance(node, ast.Try):
            # Check if try body has assignment to moe_token_dispatcher_type
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if (isinstance(target, ast.Attribute) and
                            target.attr == "moe_token_dispatcher_type"):
                            return True, "eafp_try_except"

    return False, None

found, pattern = check_moe_handling(func_node)

if found:
    print(f"BEHAVIORAL PASS: moe_token_dispatcher_type handling found (pattern: {pattern})")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: No valid moe_token_dispatcher_type handling found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- REGRESSION (15%): Verify other provider assignments preserved ----------
# [pr_diff] Pass-to-pass: existing behavior should not break
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"

def find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None

def get_all_nodes(func_node):
    all_nodes = []
    for child in ast.walk(func_node):
        all_nodes.append(child)
    return all_nodes

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = find_function(tree, "wrapped_model_provider")

if func_node is None:
    print("REGRESSION FAIL: function not found")
    sys.exit(1)

# These are the existing assignments from the PR that must still work
required_attrs = [
    "tensor_model_parallel_size",
    "pipeline_model_parallel_size",
    "expert_model_parallel_size",
    "expert_tensor_parallel_size",
    "sequence_parallel",
    "context_parallel_size",
    "variable_seq_lengths"
]

nodes = get_all_nodes(func_node)
found_attrs = set()
for node in nodes:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Attribute) and
                isinstance(target.value, ast.Name) and
                target.value.id == "provider" and
                target.attr in required_attrs):
                found_attrs.add(target.attr)

missing = set(required_attrs) - found_attrs
if not missing:
    print(f"REGRESSION PASS: all {len(required_attrs)} core provider assignments preserved")
    sys.exit(0)
else:
    print(f"REGRESSION FAIL: missing assignments for {missing}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[regression]=1; fi

# ---------- STRUCTURAL (30%): Verify placement in bridge mode block ----------
# [agent_config] Code organization - should be with other provider attrs
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model_provider.py"

def find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None

def get_all_nodes(func_node):
    all_nodes = []
    for child in ast.walk(func_node):
        all_nodes.append(child)
    return all_nodes

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = find_function(tree, "wrapped_model_provider")

if func_node is None:
    print("STRUCTURAL FAIL: wrapped_model_provider not found")
    sys.exit(1)

# Count provider attribute assignments in the function
nodes = get_all_nodes(func_node)
provider_attrs = set()
for node in nodes:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Attribute) and
                isinstance(target.value, ast.Name) and
                target.value.id == "provider"):
                provider_attrs.add(target.attr)
    # Also check setattr patterns
    if isinstance(node, ast.Call):
        if (isinstance(node.func, ast.Name) and node.func.id == "setattr"):
            if len(node.args) >= 2:
                first_arg = node.args[0]
                second_arg = node.args[1]
                if (isinstance(first_arg, ast.Name) and first_arg.id == "provider" and
                    isinstance(second_arg, ast.Constant) and
                    isinstance(second_arg.value, str)):
                    provider_attrs.add(second_arg.value)

# The fix should add moe_token_dispatcher_type alongside existing attrs
has_moe = "moe_token_dispatcher_type" in provider_attrs
has_variable_seq = "variable_seq_lengths" in provider_attrs

if has_moe and len(provider_attrs) >= 7:  # At least the original 7 + moe
    print(f"STRUCTURAL PASS: moe_token_dispatcher_type with {len(provider_attrs)} total provider attrs")
    sys.exit(0)
elif has_moe:
    print(f"STRUCTURAL PASS: moe_token_dispatcher_type found")
    sys.exit(0)
else:
    print(f"STRUCTURAL FAIL: moe_token_dispatcher_type not found (have: {provider_attrs})")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (5%): Code quality ----------
# [agent_config] (0.03): No wildcard imports - .claude/skills/*/SKILL.md:1-50 @ 7f2a03b5
grep_result=$(grep -rn "from .* import \*" "$TARGET" 2>/dev/null)
if [ -z "$grep_result" ]; then RESULTS[config_no_wildcard]=1; fi

# [agent_config] (0.02): No bare print() - .claude/skills/*/SKILL.md:1-50 @ 7f2a03b5
grep_result=$(grep -nE "^\s*print\(" "$TARGET" 2>/dev/null)
if [ -z "$grep_result" ]; then RESULTS[config_no_bare_print]=1; fi

# ---------- SCORE ----------
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral regression structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
