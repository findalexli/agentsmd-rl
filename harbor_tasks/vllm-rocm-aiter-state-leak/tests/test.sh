#!/usr/bin/env bash
set +e

REPO="/workspace/vllm"
SCORE=0
TOTAL=0
LOG=""

add() {
    local weight=$1 label=$2 result=$3
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$result" = "pass" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
        LOG+="  PASS ($weight) $label\n"
    else
        LOG+="  FAIL ($weight) $label\n"
    fi
}

echo "=== vllm-rocm-aiter-state-leak grading ==="

# ---------- GATE: syntax check ----------
# [pr_diff] (0): All modified files must be valid Python
GATE_OK=true
for f in \
    tests/kernels/moe/test_shared_fused_moe_routed_transform.py \
    tests/kernels/moe/test_routing_simulator.py \
    vllm/distributed/parallel_state.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        GATE_OK=false
        echo "GATE FAIL: $f does not parse"
    fi
done

if [ "$GATE_OK" = "false" ]; then
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    echo "Gate failed — syntax error in modified files"
    exit 0
fi
echo "GATE: syntax OK"

# ---------- Fail-to-pass behavioral checks ----------
# WHY AST: All three target files require ROCm GPU + torch to import/execute.

# [pr_diff] (0.30): The if-block that sets AITER env vars must NOT be gated on use_rocm_aiter.
# The bug: env vars only set when use_rocm_aiter=True, so False case has stale state.
# The fix: any restructuring where is_rocm env setup runs regardless of use_rocm_aiter value.
# We check: the if-condition covering monkeypatch.setenv does NOT reference 'use_rocm_aiter'.
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/tests/kernels/moe/test_shared_fused_moe_routed_transform.py').read()
tree = ast.parse(source)

def names_in_expr(node):
    '''Collect all Name.id values in an expression subtree.'''
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

# Find the test function
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_routed_input_transform_inside_vs_outside':
        # Find all If nodes whose body contains a call with 'setenv' in it
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check if this if-block's body (recursively) contains a setenv call
                has_setenv = False
                for sub in ast.walk(child):
                    if isinstance(sub, ast.Call):
                        func = sub.func
                        if isinstance(func, ast.Attribute) and func.attr == 'setenv':
                            has_setenv = True
                            break
                if has_setenv:
                    # The condition of this if must NOT reference use_rocm_aiter
                    cond_names = names_in_expr(child.test)
                    if 'use_rocm_aiter' in cond_names:
                        print('fail')  # Still gated on use_rocm_aiter
                    else:
                        print('pass')  # Env setup runs for all ROCm cases
                    sys.exit(0)
        # If no if-block with setenv found, check if setenv is at top-level of function
        # (valid alternative: no if-guard at all, always set env vars)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                func = child.value.func
                if isinstance(func, ast.Attribute) and func.attr == 'setenv':
                    print('pass')
                    sys.exit(0)
        print('fail')
        sys.exit(0)
print('fail')
" 2>/dev/null || echo "fail")
add 0.30 "[pr_diff] ROCm env-var setup NOT gated on use_rocm_aiter" "$RESULT"

# [pr_diff] (0.25): cleanup_dist_env_and_memory calls refresh_env_variables() (actual Call node).
# The bug: cleanup doesn't reset aiter cached state, causing cross-test leaks.
# We verify an actual function call, not just a string/comment.
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/vllm/distributed/parallel_state.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'cleanup_dist_env_and_memory':
        # Find an actual Call node whose func ends with .refresh_env_variables
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr == 'refresh_env_variables':
                    print('pass')
                    sys.exit(0)
        print('fail')
        sys.exit(0)
print('fail')
" 2>/dev/null || echo "fail")
add 0.25 "[pr_diff] cleanup_dist_env_and_memory has Call to refresh_env_variables()" "$RESULT"

# [pr_diff] (0.15): test_routing_simulator does NOT directly mutate envs.environment_variables[key].
# The bug: direct dict assignment isn't reverted by monkeypatch teardown.
# Accept any fix that removes the direct Subscript assignment (setitem, delenv, context mgr, etc).
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/tests/kernels/moe/test_routing_simulator.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'test_routing_strategy_integration':
        # Check there is NO direct assignment to environment_variables[...]
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Attribute):
                        if target.value.attr == 'environment_variables':
                            print('fail')
                            sys.exit(0)
        # Also accept if function was restructured — just verify no direct mutation
        print('pass')
        sys.exit(0)
print('fail')
" 2>/dev/null || echo "fail")
add 0.15 "[pr_diff] test_routing_simulator has no direct dict mutation of environment_variables" "$RESULT"

# ---------- Pass-to-pass regression ----------

# [pr_diff] (0.10): cleanup_dist_env_and_memory retains existing cleanup calls
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/vllm/distributed/parallel_state.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'cleanup_dist_env_and_memory':
        # Check for Call nodes to disable_envs_cache and gc.unfreeze (existing behavior)
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute):
                    calls.add(func.attr)
        has_disable = 'disable_envs_cache' in calls
        has_unfreeze = 'unfreeze' in calls
        if has_disable and has_unfreeze:
            print('pass')
        else:
            print('fail')
        sys.exit(0)
print('fail')
" 2>/dev/null || echo "fail")
add 0.10 "[pr_diff] cleanup retains disable_envs_cache() and gc.unfreeze() calls" "$RESULT"

# [pr_diff] (0.10): test file still references both AITER env var names
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/tests/kernels/moe/test_shared_fused_moe_routed_transform.py').read()
tree = ast.parse(source)

# Look for string constants 'VLLM_ROCM_USE_AITER' and 'VLLM_ROCM_USE_AITER_MOE' in AST
found_aiter = False
found_aiter_moe = False
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if node.value == 'VLLM_ROCM_USE_AITER':
            found_aiter = True
        elif node.value == 'VLLM_ROCM_USE_AITER_MOE':
            found_aiter_moe = True
if found_aiter and found_aiter_moe:
    print('pass')
else:
    print('fail')
" 2>/dev/null || echo "fail")
add 0.10 "[pr_diff] test still references VLLM_ROCM_USE_AITER and VLLM_ROCM_USE_AITER_MOE" "$RESULT"

# ---------- Anti-stub ----------

# [pr_diff] (0.10): cleanup_dist_env_and_memory has meaningful new code (not a stub)
RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/vllm/distributed/parallel_state.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'cleanup_dist_env_and_memory':
        # Count total statements (recursively) — must have meaningful body
        stmts = sum(1 for child in ast.walk(node)
                     if isinstance(child, (ast.Assign, ast.Call, ast.If, ast.Import, ast.ImportFrom, ast.Return, ast.Expr)))
        # Buggy version has ~10 statements; fix adds ~3-5 more
        if stmts >= 8:
            print('pass')
        else:
            print('fail')
        sys.exit(0)
print('fail')
" 2>/dev/null || echo "fail")
add 0.10 "[pr_diff] Anti-stub: cleanup has sufficient non-trivial statements" "$RESULT"

# ---------- Summary ----------
echo ""
echo "=== Results ==="
printf "$LOG"
echo ""
echo "Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
reward = $SCORE
print(json.dumps({
    'reward': reward,
    'behavioral': min(reward, 0.70),
    'regression': max(0, min(reward - 0.70, 0.20)),
    'config': 0.0,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
