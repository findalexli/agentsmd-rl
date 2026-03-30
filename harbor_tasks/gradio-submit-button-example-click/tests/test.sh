#!/usr/bin/env bash
# Verifier for gradio-submit-button-example-click
#
# Bug: Race condition between example_select handlers causes submit button
# to not be restored after clicking an example.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/gradio/gradio/chat_interface.py"

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/gradio/gradio/chat_interface.py") as f:
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
#   TEST 1 (fail-to-pass: example_select removed from event_triggers) = 0.30
#   TEST 2 (fail-to-pass: submit_btn=False in .then() chain)         = 0.30
#   TEST 3 (pass-to-pass: _setup_stop_events still called)           = 0.10
#   TEST 4 (structural: example_select_runs flag used)               = 0.15
#   TEST 5 (anti-stub)                                               = 0.10
#   TOTAL                                                            = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: example_select removed from event_triggers
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] chatbot.example_select removed from _setup_stop_events triggers"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

# Find the _setup_stop_events call and check its event_triggers list
# The fix removes self.chatbot.example_select from event_triggers
lines = src.split('\n')

# Look for the event_triggers list passed to _setup_stop_events
in_stop_events = False
trigger_lines = []
for i, line in enumerate(lines):
    if '_setup_stop_events' in line:
        in_stop_events = True
    if in_stop_events:
        trigger_lines.append(line)
        if 'events_to_cancel' in line or (']' in line and 'event_triggers' not in line):
            if len(trigger_lines) > 3:
                break

trigger_text = '\n'.join(trigger_lines)

if 'example_select' in trigger_text and 'event_triggers' in trigger_text:
    print("FAIL: chatbot.example_select still in event_triggers for _setup_stop_events")
    sys.exit(1)

# Verify _setup_stop_events is still called
if '_setup_stop_events' in src:
    print("PASS: example_select not in _setup_stop_events event_triggers")
    sys.exit(0)

print("FAIL: _setup_stop_events not found")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.30]: submit_btn=False in .then() chain
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] submit_btn=False added as .then() step in example chain"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

# The fix adds a .then() step that sets submit_btn=False
# Look for: example_select_event = example_select_event.then(... submit_btn=False ...)
if 'submit_btn=False' in src and 'example_select_event' in src:
    # Check it's in a .then() context
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'submit_btn=False' in line or ('submit_btn' in line and 'False' in line):
            # Check nearby lines for .then(
            context = '\n'.join(lines[max(0,i-5):i+5])
            if '.then(' in context and 'example_select' in context:
                print("PASS: submit_btn=False in .then() chain for example_select")
                sys.exit(0)

    # Alternative: check for submit_btn=False anywhere in _setup_events
    if 'submit_btn=False' in src:
        print("PASS: submit_btn=False found in the code")
        sys.exit(0)

print("FAIL: submit_btn=False .then() step not found")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [PASS-TO-PASS, 0.10]: _setup_stop_events still called
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] _setup_stop_events still called"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

if '_setup_stop_events' in src and 'events_to_cancel' in src:
    print("PASS: _setup_stop_events still called with events_to_cancel")
    sys.exit(0)

print("FAIL: _setup_stop_events or events_to_cancel not found")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL, 0.15]: example_select_runs flag
###############################################################################
echo ""
echo "TEST 4: [structural] example_select_runs flag used for conditional cancel"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    src = f.read()

# The fix adds: example_select_runs = True/False
# And uses it: if example_select_event is not None and example_select_runs:
if 'example_select_runs' in src:
    print("PASS: example_select_runs flag found")
    sys.exit(0)

# Alternative: any flag that conditionally adds example_select to events_to_cancel
if 'run_examples_on_click' in src and 'events_to_cancel' in src:
    print("PASS: conditional example cancellation logic found")
    sys.exit(0)

print("FAIL: example_select_runs flag or conditional cancellation not found")
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

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()

line_count = len(source.splitlines())
if line_count < 300:
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
# Source: AGENTS.md line 43 @ commit fe955348f24115744015d85639e170b8518b28c1
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/chat_interface.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T6=0; echo "TEST 6: config ruff format PASS"; else T6=1; echo "TEST 6: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.30 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: example_select removed)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: submit_btn=False .then())   = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (pass-to-pass: _setup_stop_events)         = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (structural: example_select_runs flag)     = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (anti-stub)                                = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (config: ruff format)                   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
