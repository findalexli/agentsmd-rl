#!/usr/bin/env bash
# Verifier for gradio-on-triggers-type-hints
#
# Bug: gr.on() and gr.render() triggers parameter is typed as
# EventListenerCallable which doesn't accept bound component event methods.
# Fix: add Trigger type alias that also accepts Callable[..., Dependency].
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

REWARD_JSON="/logs/verifier/reward.json"

###############################################################################
# GATE: Python syntax validity for both files
###############################################################################
python3 << 'PYEOF'
import ast, sys
for path in ["/workspace/gradio/gradio/events.py", "/workspace/gradio/gradio/renderable.py"]:
    try:
        with open(path) as f:
            ast.parse(f.read())
    except SyntaxError as e:
        print(f"GATE FAIL: {path}: {e}")
        sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    jq -n '{reward: 0.0, behavioral: 0.0, regression: 0.0, config: 0.0}' > "$REWARD_JSON"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   Fail-to-pass (type checking): 0.70
#     - mypy accepts bound methods with gr.on()          = 0.35
#     - mypy accepts bound methods with gr.render()      = 0.30
#     - mypy accepts single trigger (not just sequence)  = 0.05
#   Regression (pass-to-pass): 0.15
#     - EventListenerCallable still exists               = 0.05
#     - Original EventListenerCallable still works       = 0.10
#   Structural: 0.10
#     - Trigger alias defined correctly                  = 0.05
#     - Files are not stubs                              = 0.05
#   Config: 0.05
#     - Ruff format check
#   TOTAL                                                = 1.00
###############################################################################
SCORE=0
BEHAVIORAL=0
REGRESSION=0
STRUCTURAL=0
CONFIG=0

# Install mypy for type checking
pip install mypy --quiet 2>/dev/null

cd /workspace/gradio

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: mypy accepts bound methods with gr.on()
#
# This is the core behavioral test. The bug was that mypy rejected valid code
# using button.click, tab.select etc. After the fix, mypy should accept it.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] mypy accepts bound methods in gr.on() triggers"

cat > /tmp/test_on_triggers.py << 'TESTEOF'
"""Test that mypy accepts bound event methods as triggers for gr.on()"""
from __future__ import annotations
import gradio as gr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gradio.events import Dependency

def handler() -> str:
    return "hello"

# Test with Sequence of bound methods
with gr.Blocks() as demo:
    btn = gr.Button("Click")
    output = gr.Textbox()

    # This should NOT produce a type error after the fix
    gr.on(
        triggers=[btn.click, btn.change],
        fn=handler,
        outputs=output
    )

# Test with single bound method
with gr.Blocks() as demo2:
    btn2 = gr.Button("Click")
    output2 = gr.Textbox()

    # This should NOT produce a type error after the fix
    gr.on(
        triggers=btn2.click,
        fn=handler,
        outputs=output2
    )
TESTEOF

cd /workspace/gradio
python3 -m mypy /tmp/test_on_triggers.py --ignore-missing-imports --show-error-codes 2>&1 | head -50
MYPY_EXIT=${PIPESTATUS[0]}
echo "  -> mypy exit code: $MYPY_EXIT"

T1_BASE=0
if [ $MYPY_EXIT -eq 0 ]; then
    echo "PASS: mypy accepts bound methods in gr.on() triggers"
    T1_BASE=1
else
    echo "FAIL: mypy still rejects bound methods in gr.on() triggers"
    T1_BASE=0
fi

if [ $T1_BASE -eq 0 ]; then
    # Check specifically for the triggers-related type error
    python3 -m mypy /tmp/test_on_triggers.py --ignore-missing-imports 2>&1 | grep -E "(triggers|EventListenerCallable)" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  -> Confirmed: error related to triggers/EventListenerCallable"
    fi
fi

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.30]: mypy accepts bound methods with gr.render()
# Same behavioral test for gr.render() function.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] mypy accepts bound methods in gr.render() triggers"

cat > /tmp/test_render_triggers.py << 'TESTEOF'
"""Test that mypy accepts bound event methods as triggers for gr.render()"""
from __future__ import annotations
import gradio as gr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gradio.events import Dependency

# Test with Sequence of bound methods
with gr.Blocks() as demo:
    btn = gr.Button("Click")

    @gr.render(
        inputs=[gr.Textbox()],
        triggers=[btn.click, btn.change]
    )
    def render_content(text: str):
        gr.Textbox(value=text)

# Test with single bound method
with gr.Blocks() as demo2:
    btn2 = gr.Button("Click")

    @gr.render(
        inputs=[gr.Textbox()],
        triggers=btn2.click
    )
    def render_content2(text: str):
        gr.Textbox(value=text)
TESTEOF

cd /workspace/gradio
python3 -m mypy /tmp/test_render_triggers.py --ignore-missing-imports --show-error-codes 2>&1 | head -50
MYPY_EXIT2=${PIPESTATUS[0]}
echo "  -> mypy exit code: $MYPY_EXIT2"

T2_BASE=0
if [ $MYPY_EXIT2 -eq 0 ]; then
    echo "PASS: mypy accepts bound methods in gr.render() triggers"
    T2_BASE=1
else
    echo "FAIL: mypy still rejects bound methods in gr.render() triggers"
    T2_BASE=0
fi

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.05]: mypy accepts single trigger (not just sequence)
# Some fixes might only fix the Sequence case but not the direct callable case.
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] mypy accepts single trigger (not sequence)"

# If both previous mypy checks passed, this is covered; otherwise check specifically
if [ $MYPY_EXIT -eq 0 ] && [ $MYPY_EXIT2 -eq 0 ]; then
    T3_BASE=1
else
    # Check just the single trigger case
    cat > /tmp/test_single_trigger.py << 'TESTEOF'
"""Test single trigger (not sequence)"""
import gradio as gr

def handler() -> str:
    return "hello"

with gr.Blocks() as demo:
    btn = gr.Button("Click")
    output = gr.Textbox()
    # Single bound method, not in a list
    gr.on(triggers=btn.click, fn=handler, outputs=output)
TESTEOF
    cd /workspace/gradio
    python3 -m mypy /tmp/test_single_trigger.py --ignore-missing-imports 2>&1 > /dev/null
    if [ $? -eq 0 ]; then
        T3_BASE=1
    else
        T3_BASE=0
    fi
fi

if [ $T3_BASE -eq 1 ]; then
    echo "PASS: single trigger accepted"
else
    echo "FAIL: single trigger rejected"
fi

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.05]: EventListenerCallable still defined
# Backwards compatibility: The original type should still exist.
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] EventListenerCallable still defined"

python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'EventListenerCallable':
                found = True
                break
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == 'EventListenerCallable':
            found = True
            break

if found:
    print("PASS: EventListenerCallable still defined")
    sys.exit(0)
else:
    # Also check via simple text search as fallback
    if 'EventListenerCallable' in source:
        print("PASS: EventListenerCallable referenced in source")
        sys.exit(0)
    print("FAIL: EventListenerCallable not found")
    sys.exit(1)
PYEOF
T4=$?

###############################################################################
# TEST 5 [PASS-TO-PASS, 0.10]: Original EventListenerCallable still works
# Verify that mypy still accepts EventListenerCallable usages.
###############################################################################
echo ""
echo "TEST 5: [pass-to-pass] EventListenerCallable still works"

cat > /tmp/test_event_listener_callable.py << 'TESTEOF'
"""Test that EventListenerCallable still works (for unbound listeners)"""
from gradio.events import EventListenerCallable
from typing import Callable

# Type alias should be usable
def my_listener() -> None:
    pass

# This should not error
listener: EventListenerCallable = my_listener
TESTEOF

cd /workspace/gradio
python3 -m mypy /tmp/test_event_listener_callable.py --ignore-missing-imports 2>&1 > /dev/null
MYPY_ELC=$?

T5=1
if [ $MYPY_ELC -eq 0 ]; then
    echo "PASS: EventListenerCallable still type-checks"
else
    echo "FAIL: EventListenerCallable type-checking broken"
    T5=0
fi

###############################################################################
# TEST 6 [STRUCTURAL, 0.05]: Trigger alias defined and usable
# Structural check gated behind behavioral pass.
###############################################################################
echo ""
echo "TEST 6: [structural] Trigger type alias defined"

if [ $T1_BASE -eq 0 ] && [ $T2_BASE -eq 0 ]; then
    echo "  -> Skipping structural check (behavioral tests failed)"
    T6=1  # Give benefit of doubt, but won't affect score since others failed
else
    python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find Trigger definition
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'Trigger':
                found = True
                break
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == 'Trigger':
            found = True
            break

if found:
    print("PASS: Trigger type alias defined")
    sys.exit(0)
else:
    print("FAIL: Trigger type alias not defined")
    sys.exit(1)
PYEOF
    T6=$?
fi

###############################################################################
# TEST 7 [ANTI-STUB, 0.05]: Files not replaced with stubs
###############################################################################
echo ""
echo "TEST 7: [anti-stub] files are not stubs"

python3 << 'PYEOF'
import ast, sys

for path, min_lines in [
    ("/workspace/gradio/gradio/events.py", 200),
    ("/workspace/gradio/gradio/renderable.py", 50),
]:
    with open(path) as f:
        source = f.read()
    line_count = len(source.splitlines())
    if line_count < min_lines:
        print(f"FAIL: {path} only {line_count} lines (expected {min_lines}+)")
        sys.exit(1)
    tree = ast.parse(source)
    funcs = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    if funcs < 3:
        print(f"FAIL: {path} only {funcs} functions")
        sys.exit(1)

print("PASS: both files have expected size and structure")
sys.exit(0)
PYEOF
T7=$?

###############################################################################
# TEST 8 [CONFIG, 0.05]: Ruff format check
###############################################################################
echo ""
echo "TEST 8: [config] ruff format check"

pip install ruff --quiet 2>/dev/null
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/events.py /workspace/gradio/gradio/renderable.py 2>/dev/null
RUFF_EXIT=$?

T8=1
if [ $RUFF_EXIT -eq 0 ]; then
    echo "TEST 8: ruff format PASS"
else
    echo "TEST 8: ruff format FAIL"
    T8=0
fi

###############################################################################
# Final weighted score
###############################################################################
echo ""

T1_VAL=$(python3 -c "print(0.35 if $T1_BASE == 1 else 0.0)")
T2_VAL=$(python3 -c "print(0.30 if $T2_BASE == 1 else 0.0)")
T3_VAL=$(python3 -c "print(0.05 if $T3_BASE == 1 else 0.0)")
T4_VAL=$(python3 -c "print(0.05 if $T4 == 0 else 0.0)")
T5_VAL=$(python3 -c "print(0.10 if $T5 == 0 else 0.0)")
T6_VAL=$(python3 -c "print(0.05 if $T6 == 0 else 0.0)")
T7_VAL=$(python3 -c "print(0.05 if $T7 == 0 else 0.0)")
T8_VAL=$(python3 -c "print(0.05 if $T8 == 0 else 0.0)")

SCORE=$(python3 -c "
t1 = $T1_VAL
t2 = $T2_VAL
t3 = $T3_VAL
t4 = $T4_VAL
t5 = $T5_VAL
t6 = $T6_VAL
t7 = $T7_VAL
t8 = $T8_VAL
score = t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8
behavioral = t1 + t2 + t3
regression = t4 + t5
structural = t6 + t7
config = t8
print(f'{score:.2f} {behavioral:.2f} {regression:.2f} {structural:.2f} {config:.2f}')
")

TOTAL=$(echo $SCORE | cut -d' ' -f1)
BEHAVIORAL=$(echo $SCORE | cut -d' ' -f2)
REGRESSION=$(echo $SCORE | cut -d' ' -f3)
STRUCTURAL=$(echo $SCORE | cut -d' ' -f4)
CONFIG=$(echo $SCORE | cut -d' ' -f5)

echo "RESULT: score = $TOTAL"
echo "  TEST 1 (f2p: mypy gr.on)           = $([ $T1_BASE -eq 1 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (f2p: mypy gr.render)       = $([ $T2_BASE -eq 1 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (f2p: single trigger)       = $([ $T3_BASE -eq 1 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 4 (p2p: EventListenerCallable defined) = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 5 (p2p: ELC works)            = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (struct: Trigger defined)   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 7 (anti-stub)                 = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 8 (config: ruff format)       = $([ $T8 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo ""
echo "Breakdown: Behavioral=$BEHAVIORAL, Regression=$REGRESSION, Structural=$STRUCTURAL, Config=$CONFIG"

echo "$TOTAL" > "$REWARD_FILE"
jq -n --argjson reward "$TOTAL" --argjson behavioral "$BEHAVIORAL" --argjson regression "$REGRESSION" --argjson structural "$STRUCTURAL" --argjson config "$CONFIG" \
    '{reward: $reward, behavioral: $behavioral, regression: $regression, structural: $structural, config: $config}' > "$REWARD_JSON"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
