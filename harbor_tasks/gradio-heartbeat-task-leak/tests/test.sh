#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0

add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }
award() { PASS=$(python3 -c "print($PASS + $1)"); }

cd /workspace/gradio

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (0.00): routes.py must be valid Python
python3 -c "import ast; ast.parse(open('gradio/routes.py').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: gradio/routes.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# Fail-to-pass: Behavioral tests (0.65)
########################################

# [pr_diff] (0.30): heartbeat task reference is stored before try block
add 0.30
python3 -c "
import ast, sys

source = open('gradio/routes.py').read()
tree = ast.parse(source)

# Find the sse_stream function
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'sse_stream':
        # Check that asyncio.create_task result is assigned (not bare expression)
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                if isinstance(child.value, ast.Call):
                    func = child.value.func
                    if isinstance(func, ast.Attribute) and func.attr == 'create_task':
                        found = True
                        break
        break

if not found:
    print('FAIL: heartbeat task is not stored in a variable')
    sys.exit(1)
print('PASS: heartbeat task is stored in a variable')
" 2>&1
[ $? -eq 0 ] && award 0.30

# [pr_diff] (0.35): heartbeat task is cancelled in all exit paths
add 0.35
python3 -c "
import ast, sys

source = open('gradio/routes.py').read()
tree = ast.parse(source)

cancel_count = 0
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'sse_stream':
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr == 'cancel':
                    cancel_count += 1
        break

# The fix has 3 cancel calls: disconnect, normal completion, exception
if cancel_count < 3:
    print(f'FAIL: only {cancel_count} cancel() calls found, expected at least 3')
    sys.exit(1)
print(f'PASS: found {cancel_count} cancel() calls in sse_stream')
" 2>&1
[ $? -eq 0 ] && award 0.35

########################################
# Fail-to-pass: Integration test (0.15)
########################################

# [pr_diff] (0.15): Functional test - heartbeat task ends when SSE stream completes
add 0.15
python3 -c "
import asyncio
import sys

# Test that the heartbeat coroutine, when wrapped in a task and cancelled,
# actually stops. This validates the cancel() mechanism works correctly.
async def test_cancel_mechanism():
    heartbeat_ran = False
    cancelled = False

    async def heartbeat():
        nonlocal heartbeat_ran
        while True:
            heartbeat_ran = True
            await asyncio.sleep(0.01)

    task = asyncio.create_task(heartbeat())
    await asyncio.sleep(0.05)  # let it run
    assert heartbeat_ran, 'heartbeat never ran'

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        cancelled = True

    assert cancelled, 'task was not properly cancelled'
    assert task.cancelled() or task.done(), 'task still running after cancel'
    print('PASS: cancel mechanism works correctly')

asyncio.run(test_cancel_mechanism())
" 2>&1
[ $? -eq 0 ] && award 0.15

########################################
# Pass-to-pass: Regression (0.10)
########################################

# [repo_tests] (0.10): existing heartbeat function still defined and operational
add 0.10
python3 -c "
import ast, sys

source = open('gradio/routes.py').read()
tree = ast.parse(source)

# Verify heartbeat async function still exists
found_heartbeat = False
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'heartbeat':
        found_heartbeat = True
        break

if not found_heartbeat:
    print('FAIL: heartbeat function no longer exists')
    sys.exit(1)

# Verify sse_stream still exists
found_sse = False
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'sse_stream':
        found_sse = True
        break

if not found_sse:
    print('FAIL: sse_stream function no longer exists')
    sys.exit(1)

# Verify StreamingResponse still returned
if 'StreamingResponse' not in source:
    print('FAIL: StreamingResponse no longer used')
    sys.exit(1)

print('PASS: heartbeat and sse_stream functions intact')
" 2>&1
[ $? -eq 0 ] && award 0.10

########################################
# Config-derived (0.10)
########################################

# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:38
add 0.05
if command -v ruff &>/dev/null; then
    ruff check gradio/routes.py --select E,W --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS: ruff check passes"
        award 0.05
    else
        echo "FAIL: ruff check failed"
    fi
else
    # If ruff not available, do basic style check
    python3 -c "
import ast
ast.parse(open('gradio/routes.py').read())
print('PASS: syntax valid (ruff unavailable)')
"
    [ $? -eq 0 ] && award 0.05
fi

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:40
add 0.05
python3 -c "
import sys
source = open('gradio/routes.py').read()

# Check that the fix doesn't introduce bare prints or logging changes in sse_stream
# and that asyncio import is still at the top
if 'import asyncio' not in source:
    print('FAIL: asyncio import missing')
    sys.exit(1)

# Ensure no debugging artifacts
lines = source.split('\n')
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('print(') and 'heartbeat' in stripped.lower():
        print(f'FAIL: debug print on line {i+1}')
        sys.exit(1)
    if stripped.startswith('# TODO') and 'heartbeat' in stripped.lower():
        print(f'FAIL: TODO comment on line {i+1}')
        sys.exit(1)

print('PASS: consistent with surrounding code style')
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($PASS, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "print(round(min($PASS, 0.80), 2))")
python3 -c "
import json
reward = $REWARD
# Split into categories based on what passed
behavioral = min(reward, 0.80)
remaining = max(reward - 0.80, 0.0)
regression = min(remaining, 0.10)
remaining2 = max(remaining - 0.10, 0.0)
config = min(remaining2, 0.10)
print(json.dumps({
    'reward': round(reward, 2),
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config, 2),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

echo "Total reward: $REWARD"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
