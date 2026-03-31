#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/gradio

##############################################################################
# GATE: Syntax check — abort on failure
##############################################################################
# [pr_diff] (gate): Both changed files must parse without syntax errors
python3 -c "
import ast
ast.parse(open('client/python/gradio_client/client.py').read())
ast.parse(open('client/python/gradio_client/utils.py').read())
print('GATE: syntax OK')
" 2>&1
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax errors in changed files"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.75 total)
##############################################################################

# [pr_diff] (0.40): stream_sse_v1plus works with deque-based pending_messages
# On buggy code, pop(0) on a deque raises TypeError; on fixed code popleft works
python3 -c "
import sys, threading, queue, asyncio
from collections import deque
from unittest.mock import MagicMock
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, 'client/python')
from gradio_client.utils import stream_sse_v1plus, ServerMessage

# Build a minimal mock for Communicator
helper = MagicMock()
helper.lock = threading.Lock()
helper.thread_complete = False
helper.should_cancel = False
helper.job.outputs = []
helper.updates = queue.Queue()

event_id = 'test-deque-123'
msg = {
    'msg': ServerMessage.process_completed,
    'output': {'data': ['result_value']},
    'success': True,
}
pending = {event_id: deque([msg])}

# Call stream_sse_v1plus — fixed code uses popleft (works on deque)
# Buggy code uses pop(0) which raises TypeError on deque
result = stream_sse_v1plus(helper, pending, event_id, 'sse_v2')
assert result is not None, 'stream_sse_v1plus returned None'
assert result.get('data') == ['result_value'], f'Wrong output: {result}'
assert event_id not in pending, 'event_id should be deleted from pending after completion'
print('PASS: stream_sse_v1plus works with deque')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.40
    echo "  [PASS] stream_sse_v1plus_deque (0.40)"
else
    add_total 0.40
    echo "  [FAIL] stream_sse_v1plus_deque (0.00/0.40)"
fi

# [pr_diff] (0.35): Multi-message FIFO processing through deque
# Verifies process_generating then process_completed are consumed in order via popleft
python3 -c "
import sys, threading, queue
from collections import deque
from unittest.mock import MagicMock

sys.path.insert(0, 'client/python')
from gradio_client.utils import stream_sse_v1plus, ServerMessage

helper = MagicMock()
helper.lock = threading.Lock()
helper.thread_complete = False
helper.should_cancel = False
helper.job.outputs = []
helper.updates = queue.Queue()
helper.prediction_processor = lambda *args: args

event_id = 'test-multi-msg'
msg_generating = {
    'msg': ServerMessage.process_generating,
    'output': {'data': ['partial_result']},
    'success': True,
}
msg_completed = {
    'msg': ServerMessage.process_completed,
    'output': {'data': ['final_result']},
    'success': True,
}
# Both messages in a deque — must be processed in FIFO order
pending = {event_id: deque([msg_generating, msg_completed])}

result = stream_sse_v1plus(helper, pending, event_id, 'sse_v1')
assert result is not None, 'stream_sse_v1plus returned None'
assert result.get('data') == ['final_result'], f'Wrong final output: {result}'

# Verify both messages were consumed (deque should be deleted)
assert event_id not in pending, 'event_id should be cleaned up'

# Verify the generating message was processed first (helper.updates should have 2 items)
updates = []
while not helper.updates.empty():
    updates.append(helper.updates.get_nowait())
assert len(updates) >= 2, f'Expected at least 2 updates, got {len(updates)}'
print('PASS: multi-message FIFO via deque')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.35
    echo "  [PASS] multi_message_fifo_deque (0.35)"
else
    add_total 0.35
    echo "  [FAIL] multi_message_fifo_deque (0.00/0.35)"
fi

##############################################################################
# PASS-TO-PASS: Imports and basic functionality (0.10)
##############################################################################

# [pr_diff] (0.10): gradio_client imports work and deque is available
python3 -c "
import sys
sys.path.insert(0, 'client/python')
from gradio_client.utils import stream_sse_v1plus, get_pred_from_sse_v1plus, ServerMessage
from gradio_client.client import Client
from collections import deque
# Verify deque is importable from both modules
import gradio_client.utils as u
import gradio_client.client as c
assert hasattr(u, 'stream_sse_v1plus')
assert hasattr(u, 'get_pred_from_sse_v1plus')
print('PASS: imports OK')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "  [PASS] imports_ok (0.10)"
else
    add_total 0.10
    echo "  [FAIL] imports_ok (0.00/0.10)"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.05)
##############################################################################

# [pr_diff] (0.05): Changed files are not empty or stubbed
python3 -c "
client_py = open('client/python/gradio_client/client.py').read()
utils_py = open('client/python/gradio_client/utils.py').read()
assert len(client_py) > 1000, 'client.py looks stubbed or empty'
assert len(utils_py) > 1000, 'utils.py looks stubbed or empty'
assert 'pending_messages_per_event' in client_py, 'client.py missing key code'
assert 'stream_sse_v1plus' in utils_py, 'utils.py missing key function'
print('PASS: anti-stub OK')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "  [PASS] anti_stub (0.05)"
else
    add_total 0.05
    echo "  [FAIL] anti_stub (0.00/0.05)"
fi

##############################################################################
# CONFIG-DERIVED: ruff format check (0.10)
##############################################################################

# [agent_config] (0.10): "Python code is formatted with ruff" — AGENTS.md:43
pip install ruff >/dev/null 2>&1
ruff check client/python/gradio_client/client.py client/python/gradio_client/utils.py --select E,W --quiet 2>&1
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "  [PASS] ruff_format (0.10)"
else
    add_total 0.10
    echo "  [FAIL] ruff_format (0.00/0.10)"
fi

##############################################################################
# Summary
##############################################################################

echo ""
echo "Total: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

# Compute breakdown for reward.json
python3 -c "
import json
score = $SCORE
behavioral = min(score, 0.75)
regression = min(max(score - 0.75, 0), 0.10)
structural = min(max(score - 0.85, 0), 0.05)
config = min(max(score - 0.90, 0), 0.10)
print(json.dumps({'reward': score, 'behavioral': behavioral, 'regression': regression, 'structural': structural, 'config': config, 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
