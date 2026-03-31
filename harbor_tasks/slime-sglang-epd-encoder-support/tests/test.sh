#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/slime
LOG_DIR=/logs/verifier
mkdir -p "$LOG_DIR"
SCORE=0

# === GATE (0): Syntax check — abort on failure ===
echo "=== GATE: Syntax check ==="
if ! python3 -c "
import py_compile
py_compile.compile('$REPO/slime/backends/sglang_utils/sglang_config.py', doraise=True)
py_compile.compile('$REPO/slime/backends/sglang_utils/sglang_engine.py', doraise=True)
py_compile.compile('$REPO/slime/ray/rollout.py', doraise=True)
print('PASS: syntax OK')
"; then
    echo "FAIL: syntax error — aborting"
    echo "0.00" > "$LOG_DIR/reward.txt"
    exit 0
fi

# [pr_diff] (0.25): ServerGroupConfig accepts "encoder" as valid worker_type
echo ""
echo "=== Test 1: ServerGroupConfig accepts encoder worker_type ==="
T1=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.backends.sglang_utils.sglang_config import ServerGroupConfig
try:
    cfg = ServerGroupConfig(worker_type='encoder', num_gpus=8, num_gpus_per_engine=4)
    assert cfg.worker_type == 'encoder', f'Expected encoder, got {cfg.worker_type}'
    print('PASS')
except (AssertionError, ValueError, TypeError) as e:
    print(f'FAIL: {e}')
" 2>&1 | tail -1)
echo "$T1"
if [ "$T1" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi

# [pr_diff] (0.15): has_encoder_disaggregation property returns True for encoder groups
echo ""
echo "=== Test 2: has_encoder_disaggregation property ==="
T2=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.backends.sglang_utils.sglang_config import SglangConfig, ServerGroupConfig
cfg = SglangConfig(
    name='test',
    server_groups=[
        ServerGroupConfig(worker_type='encoder', num_gpus=8, num_gpus_per_engine=4),
        ServerGroupConfig(worker_type='prefill', num_gpus=8, num_gpus_per_engine=4),
        ServerGroupConfig(worker_type='decode', num_gpus=16, num_gpus_per_engine=4),
    ]
)
try:
    result = cfg.has_encoder_disaggregation
    if result is True:
        print('PASS')
    else:
        print(f'FAIL: expected True, got {result}')
except AttributeError as e:
    print(f'FAIL: property not found: {e}')
" 2>&1 | tail -1)
echo "$T2"
if [ "$T2" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.15): has_encoder_disaggregation returns False when no encoder groups
echo ""
echo "=== Test 3: has_encoder_disaggregation is False without encoder groups ==="
T3=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.backends.sglang_utils.sglang_config import SglangConfig, ServerGroupConfig
cfg = SglangConfig(
    name='test',
    server_groups=[
        ServerGroupConfig(worker_type='prefill', num_gpus=8, num_gpus_per_engine=4),
        ServerGroupConfig(worker_type='decode', num_gpus=16, num_gpus_per_engine=4),
    ]
)
try:
    result = cfg.has_encoder_disaggregation
    if result is False:
        print('PASS')
    else:
        print(f'FAIL: expected False, got {result}')
except AttributeError as e:
    print(f'FAIL: property not found: {e}')
" 2>&1 | tail -1)
echo "$T3"
if [ "$T3" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.15): _compute_server_args sets encoder_only=True for encoder worker_type
# WHY AST: _compute_server_args imports sglang.srt.server_args.ServerArgs which
# transitively requires torch/CUDA — cannot call this function in CPU-only container
echo ""
echo "=== Test 4: encoder_only set for encoder worker_type ==="
T4=$(python3 -c "
import ast

with open('$REPO/slime/backends/sglang_utils/sglang_engine.py') as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_compute_server_args':
        # Look for: elif worker_type == 'encoder': kwargs['encoder_only'] = True
        for child in ast.walk(node):
            if isinstance(child, ast.Compare):
                # Check for worker_type == 'encoder'
                if (isinstance(child.left, ast.Name) and child.left.id == 'worker_type'
                    and len(child.ops) == 1 and isinstance(child.ops[0], ast.Eq)
                    and len(child.comparators) == 1
                    and isinstance(child.comparators[0], ast.Constant)
                    and child.comparators[0].value == 'encoder'):
                    found = True
                    break
        break

if found:
    print('PASS')
else:
    print('FAIL: no encoder branch in _compute_server_args')
" 2>&1 | tail -1)
echo "$T4"
if [ "$T4" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.05): Override key normalization (hyphens to underscores)
# WHY AST: same function, same import constraint
echo ""
echo "=== Test 5: Override key normalization ==="
T5=$(python3 -c "
import ast

with open('$REPO/slime/backends/sglang_utils/sglang_engine.py') as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_compute_server_args':
        for child in ast.walk(node):
            # Look for .replace('-', '_') or .replace(\"-\", \"_\")
            if (isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr == 'replace'
                and len(child.args) == 2
                and isinstance(child.args[0], ast.Constant) and child.args[0].value == '-'
                and isinstance(child.args[1], ast.Constant) and child.args[1].value == '_'):
                found = True
                break
        break

if found:
    print('PASS')
else:
    print('FAIL: no hyphen-to-underscore key normalization in _compute_server_args')
" 2>&1 | tail -1)
echo "$T5"
if [ "$T5" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [pr_diff] (0.10): P2P — existing worker types still accepted
echo ""
echo "=== Test 6: P2P — existing worker types still valid ==="
T6=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.backends.sglang_utils.sglang_config import ServerGroupConfig
for wt in ['regular', 'prefill', 'decode', 'placeholder']:
    try:
        cfg = ServerGroupConfig(worker_type=wt, num_gpus=4, num_gpus_per_engine=4)
        assert cfg.worker_type == wt
    except Exception as e:
        print(f'FAIL: {wt} rejected: {e}')
        raise SystemExit(0)
print('PASS')
" 2>&1 | tail -1)
echo "$T6"
if [ "$T6" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

# [pr_diff] (0.05): P2P — has_pd_disaggregation still works
echo ""
echo "=== Test 7: P2P — has_pd_disaggregation still works ==="
T7=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.backends.sglang_utils.sglang_config import SglangConfig, ServerGroupConfig
cfg = SglangConfig(
    name='test',
    server_groups=[
        ServerGroupConfig(worker_type='prefill', num_gpus=8, num_gpus_per_engine=4),
        ServerGroupConfig(worker_type='decode', num_gpus=8, num_gpus_per_engine=4),
    ]
)
result = cfg.has_pd_disaggregation
if result is True:
    print('PASS')
else:
    print(f'FAIL: expected True, got {result}')
" 2>&1 | tail -1)
echo "$T7"
if [ "$T7" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [pr_diff] (0.05): get_url method exists in HttpServerEngineAdapter
echo ""
echo "=== Test 8: get_url method exists ==="
T8=$(python3 -c "
import ast

with open('$REPO/slime/backends/sglang_utils/sglang_engine.py') as f:
    tree = ast.parse(f.read())

# Find HttpServerEngineAdapter class and check for get_url method
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'HttpServerEngineAdapter':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'get_url':
                found = True
                break
        break

if found:
    print('PASS')
else:
    print('FAIL: get_url method not found in HttpServerEngineAdapter')
" 2>&1 | tail -1)
echo "$T8"
if [ "$T8" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [pr_diff] (0.05): launch_server_process branches on encoder_only
echo ""
echo "=== Test 9: launch_server_process handles encoder_only ==="
T9=$(python3 -c "
import ast

with open('$REPO/slime/backends/sglang_utils/sglang_engine.py') as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'launch_server_process':
        # Look for encoder_only reference
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr == 'encoder_only':
                found = True
                break
        break

if found:
    print('PASS')
else:
    print('FAIL: no encoder_only branch in launch_server_process')
" 2>&1 | tail -1)
echo "$T9"
if [ "$T9" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# --- Final score ---
echo ""
echo "=== Final Score ==="
SCORE=$(python3 -c "print(f'{min(1.0, $SCORE):.2f}')")
echo "Deterministic score: $SCORE"
echo "$SCORE" > "$LOG_DIR/reward.txt"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
