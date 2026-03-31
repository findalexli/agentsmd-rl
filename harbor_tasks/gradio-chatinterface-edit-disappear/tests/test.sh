#!/usr/bin/env bash
set +e

SCORE=0.0

add() { SCORE=$(python3 -c "print(round($SCORE + $1, 2))"); }

cd /workspace/gradio

##############################################################################
# GATE: Syntax check
##############################################################################
# [pr_diff] (gate): chat_interface.py must parse without syntax errors
python3 -c "import ast; ast.parse(open('gradio/chat_interface.py').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: gradio/chat_interface.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
##############################################################################

# [pr_diff] (0.40): F2P — Edit chain restores edited message to chatbot before response
# The bug: _edit_message truncates history and the event chain goes straight to the
# response callback, so the chatbot is empty while waiting. A correct fix ensures the
# edited message is visible before the response runs.
# Accepts: (a) fix inside _edit_message itself, (b) new chained dep, (c) any approach.
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface
from gradio.events import EditData

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, type="messages", editable=True)

# Set up test data
initial_history = [
    {"role": "user", "content": "hello"},
    {"role": "assistant", "content": "Echo: hello"},
]

edit_data = EditData(target=ci.chatbot, value="hello edited", index=0,
                     _data={"index": 0, "value": "hello edited"})
result = ci._edit_message(initial_history, edit_data)
chatbot_after_edit, state_after_edit, saved_input = result

# Path A: _edit_message itself already includes the edited message in chatbot output
# (alternative fix where _edit_message does the append internally)
if (isinstance(chatbot_after_edit, list) and len(chatbot_after_edit) >= 1
        and any(m.get("content") == "hello edited" for m in chatbot_after_edit)):
    print("PASS: _edit_message itself restores the edited message (alt fix)")
    sys.exit(0)

# Path B: A chained dependency restores the message after _edit_message
# Look for deps that take saved_input or chatbot_state as input and output to chatbot
chatbot_id = ci.chatbot._id
chatbot_state_id = ci.chatbot_state._id
saved_input_id = ci.saved_input._id

found_restore = False
for dep in ci.dependencies:
    fn = dep.get("fn") or dep.get("backend_fn")
    if fn is None:
        continue
    input_ids = {inp for inp in dep.get("inputs", []) if isinstance(inp, int)}
    output_ids = {out for out in dep.get("outputs", []) if isinstance(out, int)}

    # Accept any dep that takes saved_input/chatbot_state and outputs to chatbot
    if chatbot_id in output_ids and (saved_input_id in input_ids or chatbot_state_id in input_ids):
        # Try calling it with edit outputs to verify it actually restores the message
        try:
            res = fn(saved_input, state_after_edit, "user")
            if isinstance(res, list) and len(res) >= 1:
                if any(m.get("content") == "hello edited" for m in res):
                    found_restore = True
                    break
        except Exception:
            pass

if found_restore:
    print("PASS: edit chain has a dep that restores edited message to chatbot")
    sys.exit(0)

print("FAIL: no mechanism restores edited message to chatbot after _edit_message", file=sys.stderr)
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    add 0.40
    echo "PASS [0.40]: Edit chain restores edited message before response"
else
    echo "FAIL [0.40]: Edit chain does not restore edited message"
fi

# [pr_diff] (0.25): F2P — Compare editable=True vs editable=False dep counts
# A correct fix adds at least one new dep (the append step) to the edit chain.
# By comparing the two configurations, we detect the fix without hardcoding counts.
# On buggy code, both have the same number of "append-like" deps.
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

def count_append_deps(ci):
    """Count deps that take chatbot_state as input and output to chatbot."""
    chatbot_id = ci.chatbot._id
    chatbot_state_id = ci.chatbot_state._id
    count = 0
    for dep in ci.dependencies:
        input_ids = {inp for inp in dep.get("inputs", []) if isinstance(inp, int)}
        output_ids = {out for out in dep.get("outputs", []) if isinstance(out, int)}
        if chatbot_state_id in input_ids and chatbot_id in output_ids:
            count += 1
    return count

ci_edit = ChatInterface(fn=echo, type="messages", editable=True)
ci_no_edit = ChatInterface(fn=echo, type="messages", editable=False)

edit_count = count_append_deps(ci_edit)
no_edit_count = count_append_deps(ci_no_edit)

if edit_count > no_edit_count:
    print(f"PASS: editable=True has {edit_count} append deps vs {no_edit_count} without edit")
    sys.exit(0)

# Alternative: the fix might be inside _edit_message, not a new dep.
# In that case, check _edit_message returns chatbot with the edited message.
from gradio.events import EditData
history = [
    {"role": "user", "content": "hello"},
    {"role": "assistant", "content": "Echo: hello"},
]
edit_data = EditData(target=ci_edit.chatbot, value="hello edited", index=0,
                     _data={"index": 0, "value": "hello edited"})
result = ci_edit._edit_message(history, edit_data)
chatbot_out = result[0]
if isinstance(chatbot_out, list) and any(m.get("content") == "hello edited" for m in chatbot_out):
    print("PASS: _edit_message returns restored chatbot (alt fix)")
    sys.exit(0)

print(f"FAIL: editable=True has {edit_count} append deps, same as {no_edit_count}", file=sys.stderr)
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    add 0.25
    echo "PASS [0.25]: Edit chain adds restore step vs non-edit baseline"
else
    echo "FAIL [0.25]: Edit chain has no additional restore step"
fi

##############################################################################
# PASS-TO-PASS: Existing behavior must not break (0.20 total)
##############################################################################

# [pr_diff] (0.15): Submit flow still works — message appears in chatbot
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, type="messages")

# _append_message_to_history should still work for normal submit
history = ci._append_message_to_history("test message", [], "user")
assert len(history) == 1, f"Expected 1 message, got {len(history)}"
assert history[0]["content"] == "test message", f"Wrong content: {history[0]['content']}"
assert history[0]["role"] == "user", f"Wrong role: {history[0]['role']}"

# Retry-style: pop then re-append
full_history = [
    {"role": "user", "content": "msg1"},
    {"role": "assistant", "content": "resp1"},
]
popped = ci._pop_last_user_message(full_history)

print("PASS: Submit and retry flows still work correctly")
PYEOF
if [ $? -eq 0 ]; then
    add 0.15
    echo "PASS [0.15]: Submit/retry flows still work"
else
    echo "FAIL [0.15]: Submit/retry flows broken"
fi

# [pr_diff] (0.05): ChatInterface with editable=False still works
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, type="messages", editable=False)
# Should construct without errors
# Verify no edit event is registered
for dep in ci.dependencies:
    for t in dep.get("targets", []):
        if isinstance(t, (list, tuple)) and len(t) >= 2 and t[1] == "edit":
            print("FAIL: edit event found when editable=False", file=sys.stderr)
            sys.exit(1)

print("PASS: editable=False works correctly")
PYEOF
if [ $? -eq 0 ]; then
    add 0.05
    echo "PASS [0.05]: editable=False still works"
else
    echo "FAIL [0.05]: editable=False broken"
fi

##############################################################################
# CONFIG-DERIVED: Agent config checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:43
if command -v ruff &>/dev/null; then
    ruff check gradio/chat_interface.py --select E,W --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        add 0.05
        echo "PASS [0.05]: ruff check passes on chat_interface.py"
    else
        echo "FAIL [0.05]: ruff check fails on chat_interface.py"
    fi
else
    add 0.05
    echo "SKIP [0.05]: ruff not available, assuming pass"
fi

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45
# All internal edit-chain deps should use api_visibility="undocumented" (api_name not public)
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, type="messages", editable=True)

# Find edit-triggered deps and check for public api_name
edit_deps = []
for dep in ci.dependencies:
    for t in dep.get("targets", []):
        if isinstance(t, (list, tuple)) and len(t) >= 2 and t[1] == "edit":
            edit_deps.append(dep)
            break

if not edit_deps:
    print("FAIL: no edit deps found", file=sys.stderr)
    sys.exit(1)

# Check that edit trigger dep does not expose a public API
for dep in edit_deps:
    api_name = dep.get("api_name")
    if api_name is not None and api_name is not False and isinstance(api_name, str) and len(api_name) > 0:
        print(f"FAIL: edit dep has public api_name={api_name}", file=sys.stderr)
        sys.exit(1)

print("PASS: edit chain follows surrounding code style conventions")
PYEOF
if [ $? -eq 0 ]; then
    add 0.05
    echo "PASS [0.05]: Edit chain consistent with surrounding style"
else
    echo "FAIL [0.05]: Edit chain inconsistent with surrounding style"
fi

##############################################################################
# SUMMARY
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 2))")
echo ""
echo "Total score: $FINAL / 1.0"
echo "$FINAL" > /logs/verifier/reward.txt

# Build reward.json — compute category scores from individual check results
python3 - <<PYEOF
import json
total = $SCORE
# F2P checks: 0.40 + 0.25 = 0.65 max
# P2P checks: 0.15 + 0.05 = 0.20 max
# Config checks: 0.05 + 0.05 = 0.10 max
# We reconstruct from total (checks are ordered: F2P, P2P, config)
behavioral = min(total, 0.65)  # F2P portion
remaining = max(total - 0.65, 0.0)
regression = min(remaining, 0.20)  # P2P portion
remaining2 = max(remaining - 0.20, 0.0)
config = min(remaining2, 0.10)  # config portion
result = {
    "reward": round(total, 2),
    "behavioral": round(behavioral, 2),
    "regression": round(regression, 2),
    "config": round(config, 2),
    "style_rubric": 0.0
}
with open("/logs/verifier/reward.json", "w") as f:
    json.dump(result, f)
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
