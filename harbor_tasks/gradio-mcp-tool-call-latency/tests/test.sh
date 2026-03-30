#!/usr/bin/env bash
# Verifier for gradio-mcp-tool-call-latency
#
# Bug: MCP tool calls for non-queued events use HTTP loopback, adding ~4s latency.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/gradio/gradio/mcp.py"

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/gradio/gradio/mcp.py") as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: direct process_api call for non-queued) = 0.35
#   TEST 2 (fail-to-pass: SessionState import)                    = 0.20
#   TEST 3 (fail-to-pass: queue check branching)                  = 0.15
#   TEST 4 (pass-to-pass: HTTP loopback preserved for queued)     = 0.15
#   TEST 5 (anti-stub)                                            = 0.10
#   TOTAL                                                         = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: blocks.process_api() used for non-queued
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] blocks.process_api() called for non-queued events"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/mcp.py") as f:
    src = f.read()

# The fix adds: blocks.process_api(block_fn=block_fn, inputs=..., state=session_state, ...)
if 'process_api' in src and 'block_fn' in src:
    # Verify it's a direct call, not just a comment
    lines = src.split('\n')
    for line in lines:
        stripped = line.strip()
        if 'process_api' in stripped and not stripped.startswith('#'):
            print("PASS: blocks.process_api() call found")
            sys.exit(0)

print("FAIL: blocks.process_api() not found")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.20]: SessionState import
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] SessionState imported from gradio.state_holder"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/mcp.py") as f:
    src = f.read()

if 'SessionState' in src and 'state_holder' in src:
    print("PASS: SessionState imported from gradio.state_holder")
    sys.exit(0)

if 'from gradio.state_holder import SessionState' in src:
    print("PASS: SessionState import found")
    sys.exit(0)

print("FAIL: SessionState import not found")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: Queue check branching
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] branching on block_fn.queue"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/mcp.py") as f:
    src = f.read()

# The fix checks: if not block_fn.queue: ... else: ...
if 'block_fn.queue' in src:
    # Find the call_tool method and check for branching
    if ('not block_fn.queue' in src or 'block_fn.queue is False' in src or
        'if block_fn.queue' in src):
        print("PASS: branching on block_fn.queue found")
        sys.exit(0)

print("FAIL: no branching on block_fn.queue found")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.15]: HTTP loopback path preserved for queued events
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] client.submit still used for queued path"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/mcp.py") as f:
    src = f.read()

if 'client.submit' in src or '.submit(' in src:
    print("PASS: client.submit still present for queued path")
    sys.exit(0)

if '_get_or_create_client' in src:
    print("PASS: HTTP loopback client creation preserved")
    sys.exit(0)

print("FAIL: HTTP loopback path not preserved")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.10]: File is not a stub
###############################################################################
echo ""
echo "TEST 5: [anti-stub] file has substantial content"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/mcp.py") as f:
    source = f.read()

line_count = len(source.splitlines())
if line_count < 100:
    print(f"FAIL: only {line_count} lines")
    sys.exit(1)

tree = ast.parse(source)
classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
if classes < 1:
    print(f"FAIL: only {classes} classes")
    sys.exit(1)

print(f"PASS: {line_count} lines, {classes} classes")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit b1f62c0ebc09be80aee830e26689ab70b939cf44
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/mcp.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T6=0; echo "TEST 6: config ruff format PASS"; else T6=1; echo "TEST 6: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.20 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: direct process_api)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (fail-to-pass: SessionState import)    = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 3 (fail-to-pass: queue branching)        = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: submit preserved)       = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (anti-stub)                            = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (config: ruff format)                   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
