#!/usr/bin/env bash
set +e

REPO="/workspace/slime"
DIST_FILE="$REPO/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py"
ROLLOUT_FILE="$REPO/slime/ray/rollout.py"

total=0
earned=0

add() {
    local weight="$1" result="$2"
    total=$(python3 -c "print($total + $weight)")
    if [ "$result" = "1" ]; then
        earned=$(python3 -c "print($earned + $weight)")
        echo "  PASS (+$weight)"
    else
        echo "  FAIL (+0 / $weight)"
    fi
}

# ─── GATE: syntax check ───
echo "=== GATE: Python syntax check ==="
# [pr_diff] (gate): Both changed files must be valid Python
if python3 -c "
import ast, sys
for f in ['$DIST_FILE', '$ROLLOUT_FILE']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}', file=sys.stderr)
        sys.exit(1)
"; then
    echo "  GATE PASSED"
else
    echo "  GATE FAILED — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ─── FAIL-TO-PASS: keyword arguments in remote() call ───

# [pr_diff] (0.30): All init_weights_update_group.remote() calls inside
# connect_rollout_engines_from_distributed use keyword args (not positional)
echo "=== CHECK: keyword args in remote() call (scoped to function) ==="
# AST justified: Ray .remote() call requires Ray cluster + GPUs to execute
result=$(python3 -c "
import ast, sys

source = open('$DIST_FILE').read()
tree = ast.parse(source)

# Find connect_rollout_engines_from_distributed function
target_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'connect_rollout_engines_from_distributed':
            target_func = node
            break

if target_func is None:
    print('0')
    sys.exit(0)

# Find ALL init_weights_update_group.remote() calls WITHIN this function
calls_found = 0
calls_with_kwargs = 0

for node in ast.walk(target_func):
    if not isinstance(node, ast.Call):
        continue
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == 'remote'):
        continue
    inner = func.value
    if not (isinstance(inner, ast.Attribute) and inner.attr == 'init_weights_update_group'):
        continue

    calls_found += 1
    # Count positional args (excluding self-like first arg patterns)
    # The 5 core params must be keyword, not positional
    kw_names = {kw.arg for kw in node.keywords if kw.arg is not None}
    required = {'master_address', 'master_port', 'rank_offset', 'world_size', 'group_name'}
    # All required params must be kwargs AND there should be no more than 0 positional args
    # (backend='nccl' may also be keyword)
    if required.issubset(kw_names) and len(node.args) == 0:
        calls_with_kwargs += 1

# Must find at least one call, and ALL must use kwargs
if calls_found > 0 and calls_found == calls_with_kwargs:
    print('1')
else:
    print('0')
" 2>/dev/null || echo "0")
add 0.30 "$result"

# ─── FAIL-TO-PASS: SGLANG_JIT_DEEPGEMM_PRECOMPILE default ───

# [pr_diff] (0.25): Inside start_engines method, SGLANG_JIT_DEEPGEMM_PRECOMPILE
# has default value 'true' (was 'false' in buggy code)
echo "=== CHECK: PRECOMPILE default is 'true' in start_engines ==="
# AST justified: start_engines is a method on a class requiring Ray to instantiate
result=$(python3 -c "
import ast, sys

source = open('$ROLLOUT_FILE').read()
tree = ast.parse(source)

# Find start_engines method
start_engines = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'start_engines':
            start_engines = node
            break

if start_engines is None:
    print('0')
    sys.exit(0)

# Within start_engines, find dict containing SGLANG_JIT_DEEPGEMM_PRECOMPILE
# and check its value is 'true'
found = False
for node in ast.walk(start_engines):
    if not isinstance(node, ast.Dict):
        continue
    for key, val in zip(node.keys, node.values):
        if key is None:
            continue
        if isinstance(key, ast.Constant) and key.value == 'SGLANG_JIT_DEEPGEMM_PRECOMPILE':
            if isinstance(val, ast.Constant) and str(val.value).lower() == 'true':
                found = True

print('1' if found else '0')
" 2>/dev/null || echo "0")
add 0.25 "$result"

# ─── FAIL-TO-PASS: SGLANG_JIT_DEEPGEMM_FAST_WARMUP added ───

# [pr_diff] (0.20): Inside start_engines method, SGLANG_JIT_DEEPGEMM_FAST_WARMUP
# exists with default value 'true' (missing in buggy code)
echo "=== CHECK: FAST_WARMUP present with 'true' in start_engines ==="
# AST justified: same as above, embedded in Ray-dependent method
result=$(python3 -c "
import ast, sys

source = open('$ROLLOUT_FILE').read()
tree = ast.parse(source)

start_engines = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'start_engines':
            start_engines = node
            break

if start_engines is None:
    print('0')
    sys.exit(0)

found = False
for node in ast.walk(start_engines):
    if not isinstance(node, ast.Dict):
        continue
    for key, val in zip(node.keys, node.values):
        if key is None:
            continue
        if isinstance(key, ast.Constant) and key.value == 'SGLANG_JIT_DEEPGEMM_FAST_WARMUP':
            if isinstance(val, ast.Constant) and str(val.value).lower() == 'true':
                found = True

print('1' if found else '0')
" 2>/dev/null || echo "0")
add 0.20 "$result"

# ─── PASS-TO-PASS: Existing env vars preserved ───

# [pr_diff] (0.10): Existing env vars in start_engines still present
echo "=== CHECK: Existing env vars preserved in start_engines ==="
result=$(python3 -c "
import ast, sys

source = open('$ROLLOUT_FILE').read()
tree = ast.parse(source)

start_engines = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'start_engines':
            start_engines = node
            break

if start_engines is None:
    print('0')
    sys.exit(0)

required_vars = {
    'SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK',
    'SGLANG_DISABLE_TP_MEMORY_INBALANCE_CHECK',
    'SGLANG_MEMORY_SAVER_CUDA_GRAPH',
    'SGLANG_BATCH_INVARIANT_OPS_ENABLE_MM_FALLBACK_VARIANT',
}
found_vars = set()

for node in ast.walk(start_engines):
    if isinstance(node, ast.Dict):
        for key in node.keys:
            if key is not None and isinstance(key, ast.Constant) and isinstance(key.value, str):
                found_vars.add(key.value)

print('1' if required_vars.issubset(found_vars) else '0')
" 2>/dev/null || echo "0")
add 0.10 "$result"

# ─── PASS-TO-PASS: connect function still exists ───

# [pr_diff] (0.05): connect_rollout_engines_from_distributed function preserved
echo "=== CHECK: connect function preserved ==="
result=$(python3 -c "
import ast

source = open('$DIST_FILE').read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'connect_rollout_engines_from_distributed':
            # Must have non-trivial body (>5 statements to reject stubs)
            stmts = [n for n in ast.walk(node) if isinstance(n, ast.stmt)]
            if len(stmts) > 5:
                found = True

print('1' if found else '0')
" 2>/dev/null || echo "0")
add 0.05 "$result"

# ─── ANTI-STUB: File sizes ───

# [pr_diff] (0.10): Files are not truncated or replaced with stubs
echo "=== CHECK: Files not truncated ==="
result=$(python3 -c "
import os
dist_size = os.path.getsize('$DIST_FILE')
rollout_size = os.path.getsize('$ROLLOUT_FILE')
# Original files are ~12KB and ~28KB; reject anything below 60%
ok = dist_size > 7000 and rollout_size > 16000
print('1' if ok else '0')
" 2>/dev/null || echo "0")
add 0.10 "$result"

# ─── RESULTS ───
echo ""
echo "=== FINAL SCORE ==="
reward=$(python3 -c "print(round($earned / $total, 4) if $total > 0 else 0.0)")
echo "earned=$earned total=$total reward=$reward"

echo "$reward" > /logs/verifier/reward.txt
python3 -c "
import json
data = {
    'reward': $reward,
    'earned': $earned,
    'total': $total,
    'behavioral': round(min($earned, 0.75) / $total, 4) if $total > 0 else 0.0,
    'regression': round(min(max($earned - 0.75, 0), 0.15) / $total, 4) if $total > 0 else 0.0,
}
print(json.dumps(data))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
