#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
REPO="/workspace/slime"

ENGINE="$REPO/slime/backends/sglang_utils/sglang_engine.py"
ROLLOUT_RAY="$REPO/slime/ray/rollout.py"
ROLLOUT_SGLANG="$REPO/slime/rollout/sglang_rollout.py"
WANDB="$REPO/slime/utils/wandb_utils.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): All changed files must be valid Python
for f in "$ENGINE" "$ROLLOUT_RAY" "$ROLLOUT_SGLANG" "$WANDB"; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "FAIL: Syntax error in $(basename $f)"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "PASS: All files syntax OK"

echo ""
echo "=== Behavioral: enable_metrics always set in server kwargs ==="
# WHY AST: _compute_server_args imports sglang, ray, torch — unavailable in CPU container.

# [pr_diff] (0.15): enable_metrics must be True in the kwargs dict
python3 -c "
import ast

source = open('$ENGINE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_compute_server_args':
        # Find the kwargs dict — look for Dict nodes containing 'enable_metrics'
        for child in ast.walk(node):
            if isinstance(child, ast.Dict):
                keys = [k.value if isinstance(k, ast.Constant) else None for k in child.keys]
                if 'enable_metrics' in keys:
                    idx = keys.index('enable_metrics')
                    val = child.values[idx]
                    assert isinstance(val, ast.Constant) and val.value is True, \
                        f'enable_metrics must be True, got {ast.dump(val)}'
                    print('PASS: enable_metrics=True in server kwargs')
                    exit(0)
        print('FAIL: enable_metrics not found in _compute_server_args kwargs dict')
        exit(1)
print('FAIL: _compute_server_args function not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

# [pr_diff] (0.10): enable_metrics must be in PASSTHROUGH_SERVER_ARGS list
python3 -c "
import ast

source = open('$ENGINE').read()
tree = ast.parse(source)

for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'PASSTHROUGH_SERVER_ARGS':
                if isinstance(node.value, ast.List):
                    elts = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                    assert 'enable_metrics' in elts, f'enable_metrics not in PASSTHROUGH_SERVER_ARGS: {elts}'
                    print('PASS: enable_metrics in PASSTHROUGH_SERVER_ARGS')
                    exit(0)
print('FAIL: PASSTHROUGH_SERVER_ARGS not found or missing enable_metrics')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

echo ""
echo "=== Behavioral: Metrics router addr not gated on sglang_enable_metrics ==="
# WHY AST: _get_metrics_router_addr is a method on a Ray actor class — cannot instantiate without Ray.

# [pr_diff] (0.15): _get_metrics_router_addr must not early-return when sglang_enable_metrics is unset
python3 -c "
import ast

source = open('$ROLLOUT_RAY').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_get_metrics_router_addr':
        # Check that the source does NOT contain 'sglang_enable_metrics'
        func_source = ast.get_source_segment(source, node)
        if func_source is None:
            # Fallback: check by line range
            lines = source.splitlines()
            func_source = '\n'.join(lines[node.lineno-1:node.end_lineno])
        assert 'sglang_enable_metrics' not in func_source, \
            '_get_metrics_router_addr still checks sglang_enable_metrics'
        print('PASS: _get_metrics_router_addr no longer gates on sglang_enable_metrics')
        exit(0)
print('FAIL: _get_metrics_router_addr not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

echo ""
echo "=== Behavioral: W&B metrics forwarding not gated on flag ==="
# WHY AST: init_wandb_secondary imports wandb, ray — unavailable in CPU container.

# [pr_diff] (0.10): wandb_utils must forward metrics when router_addr is set, without checking sglang_enable_metrics
python3 -c "
import ast

source = open('$WANDB').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'init_wandb_secondary':
        func_source = ast.get_source_segment(source, node)
        if func_source is None:
            lines = source.splitlines()
            func_source = '\n'.join(lines[node.lineno-1:node.end_lineno])
        assert 'sglang_enable_metrics' not in func_source, \
            'init_wandb_secondary still checks sglang_enable_metrics'
        # Verify it still checks router_addr is not None
        assert 'router_addr' in func_source, \
            'init_wandb_secondary must still check router_addr'
        print('PASS: wandb metrics forwarding gated only on router_addr presence')
        exit(0)
print('FAIL: init_wandb_secondary not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

echo ""
echo "=== Behavioral: dp_rank_context removed from SGLangRolloutState ==="
# WHY AST: SGLangRolloutState imports sglang, ray, numpy — heavy deps unavailable in container.

# [pr_diff] (0.10): dp_rank_context method must be removed
python3 -c "
import ast

source = open('$ROLLOUT_SGLANG').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SGLangRolloutState':
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        assert 'dp_rank_context' not in methods, \
            f'dp_rank_context should be removed, but still found in methods: {methods}'
        print(f'PASS: dp_rank_context removed (remaining methods: {methods})')
        exit(0)
print('FAIL: SGLangRolloutState class not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# [pr_diff] (0.10): generate_and_rm must not use dp_rank_context
python3 -c "
import ast

source = open('$ROLLOUT_SGLANG').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'generate_and_rm':
        func_source = ast.get_source_segment(source, node)
        if func_source is None:
            lines = source.splitlines()
            func_source = '\n'.join(lines[node.lineno-1:node.end_lineno])
        assert 'dp_rank_context' not in func_source, \
            'generate_and_rm still references dp_rank_context'
        print('PASS: generate_and_rm no longer uses dp_rank_context')
        exit(0)
print('FAIL: generate_and_rm not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

echo ""
echo "=== Behavioral: contextmanager import removed with dead code ==="

# [pr_diff] (0.05): contextmanager import should be removed since dp_rank_context is gone
python3 -c "
source = open('$ROLLOUT_SGLANG').read()
assert 'from contextlib import contextmanager' not in source, \
    'contextmanager import still present but dp_rank_context was the only user'
print('PASS: contextmanager import removed')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# [agent_config] (0.05): "Keep test scope small and behavior-focused" — .claude/skills/add-tests-and-ci/SKILL.md:25
# Verify the fix touches only the expected files (no unnecessary changes)
CHANGED_FILES=$(cd "$REPO" && git diff --name-only HEAD 2>/dev/null | wc -l)
if [ "$CHANGED_FILES" -le 5 ]; then
    echo "PASS: Changes contained ($CHANGED_FILES files modified)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: Too many files changed ($CHANGED_FILES)"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

echo ""
echo "=== Regression: Key functions and classes still exist ==="

# [pr_diff] (0.10): All key functions/classes must still be present after changes
python3 -c "
import ast

# Check sglang_engine.py
src = open('$ENGINE').read()
tree = ast.parse(src)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
assert '_compute_server_args' in funcs, 'Missing _compute_server_args'

# Check rollout.py still has _get_metrics_router_addr
src = open('$ROLLOUT_RAY').read()
tree = ast.parse(src)
methods = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
assert '_get_metrics_router_addr' in methods, 'Missing _get_metrics_router_addr'

# Check sglang_rollout.py still has key parts
src = open('$ROLLOUT_SGLANG').read()
tree = ast.parse(src)
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
assert 'SGLangRolloutState' in classes, 'Missing SGLangRolloutState class'
funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
assert 'generate_and_rm' in funcs, 'Missing generate_and_rm'
assert 'reset' in funcs, 'Missing reset method'

# Check wandb_utils.py still has init_wandb_secondary
src = open('$WANDB').read()
tree = ast.parse(src)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
assert 'init_wandb_secondary' in funcs, 'Missing init_wandb_secondary'

print('PASS: All key functions and classes present')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

echo ""
echo "=== Structural: Anti-stub / file integrity ==="

# [pr_diff] (0.10): Changed files must not be truncated stubs
python3 -c "
import os

files = {
    '$ENGINE': 200,
    '$ROLLOUT_RAY': 100,
    '$ROLLOUT_SGLANG': 100,
    '$WANDB': 50,
}
for path, min_lines in files.items():
    lines = len(open(path).readlines())
    assert lines >= min_lines, f'{os.path.basename(path)} looks truncated: {lines} lines (expected >= {min_lines})'
print('PASS: All files have expected minimum size')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

echo ""
echo "==================================="
echo "Total: $SCORE / 1.00"
echo "==================================="

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
json.dump({
    'reward': score,
    'behavioral': min(score, 0.75),
    'regression': min(max(score - 0.75, 0), 0.10),
    'structural': min(max(score - 0.85, 0), 0.10),
    'config': min(max(score - 0.90, 0), 0.05),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
