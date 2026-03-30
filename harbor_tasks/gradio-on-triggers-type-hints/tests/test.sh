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
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: Trigger type alias in events.py)    = 0.25
#   TEST 2 (fail-to-pass: gr.on uses Trigger not EventList.)  = 0.25
#   TEST 3 (fail-to-pass: gr.render uses Trigger)             = 0.20
#   TEST 4 (pass-to-pass: EventListenerCallable still exists) = 0.10
#   TEST 5 (structural: Trigger includes Callable[..., Dep])  = 0.10
#   TEST 6 (anti-stub)                                        = 0.05
#   TOTAL                                                     = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.25]: Trigger type alias exists in events.py
#
# In buggy code, there is no Trigger type alias. The fix adds:
#   Trigger = Union[EventListenerCallable, Callable[..., Dependency]]
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] Trigger type alias defined in events.py"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

# Check for 'Trigger' as a module-level or class-level assignment
tree = ast.parse(source)

trigger_found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'Trigger':
                trigger_found = True
                break
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == 'Trigger':
            trigger_found = True

if not trigger_found:
    # Also check via text for TypeAlias style: Trigger: TypeAlias = ...
    # or simple Trigger = Union[...]
    if 'Trigger' in source and ('Union' in source or 'Callable' in source):
        # Check if Trigger is defined as a name binding
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith('Trigger') and '=' in stripped:
                trigger_found = True
                break

if trigger_found:
    print("PASS: Trigger type alias found in events.py")
    sys.exit(0)
else:
    print("FAIL: no Trigger type alias found in events.py")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: gr.on() uses Trigger (not EventListenerCallable)
#
# In buggy code, the on() function signature has:
#   triggers: Sequence[EventListenerCallable] | EventListenerCallable | None
# After fix, it should use Trigger instead.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] gr.on() triggers parameter uses Trigger type"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the on() function
on_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'on':
        on_func = node
        break

if on_func is None:
    print("FAIL: on() function not found")
    sys.exit(1)

# Get the source text of the triggers parameter annotation
# Find 'triggers' parameter
triggers_param = None
for arg in on_func.args.args:
    if arg.arg == 'triggers':
        triggers_param = arg
        break

if triggers_param is None:
    print("FAIL: triggers parameter not found in on() function")
    sys.exit(1)

# Check the annotation source text
annotation = triggers_param.annotation
if annotation is None:
    print("FAIL: triggers parameter has no type annotation")
    sys.exit(1)

# Get the source segment for the annotation
ann_source = ast.get_source_segment(source, annotation) or ""

# Check that it uses Trigger (not EventListenerCallable directly)
if 'Trigger' in ann_source and 'EventListenerCallable' not in ann_source:
    print(f"PASS: on() triggers uses Trigger type: {ann_source}")
    sys.exit(0)
elif 'Callable' in ann_source and 'Dependency' in ann_source:
    # Alternative: inline Union with Callable[..., Dependency]
    print(f"PASS: on() triggers uses inline Callable type: {ann_source}")
    sys.exit(0)
else:
    print(f"FAIL: on() triggers still uses EventListenerCallable: {ann_source}")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.20]: gr.render() uses Trigger (not EventListenerCallable)
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] gr.render() triggers parameter uses Trigger type"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/renderable.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the render() function
render_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'render':
        render_func = node
        break

if render_func is None:
    print("FAIL: render() function not found")
    sys.exit(1)

# Find 'triggers' parameter
triggers_param = None
for arg in render_func.args.args:
    if arg.arg == 'triggers':
        triggers_param = arg
        break

if triggers_param is None:
    print("FAIL: triggers parameter not found in render() function")
    sys.exit(1)

annotation = triggers_param.annotation
if annotation is None:
    print("FAIL: triggers parameter has no type annotation")
    sys.exit(1)

ann_source = ast.get_source_segment(source, annotation) or ""

if 'Trigger' in ann_source and 'EventListenerCallable' not in ann_source:
    print(f"PASS: render() triggers uses Trigger type: {ann_source}")
    sys.exit(0)
elif 'Callable' in ann_source and 'Dependency' in ann_source:
    print(f"PASS: render() triggers uses inline Callable type: {ann_source}")
    sys.exit(0)
else:
    print(f"FAIL: render() triggers still uses EventListenerCallable: {ann_source}")
    sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: EventListenerCallable still defined
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] EventListenerCallable type still defined in events.py"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

if 'EventListenerCallable' in source:
    print("PASS: EventListenerCallable still defined")
    sys.exit(0)
else:
    print("FAIL: EventListenerCallable removed from events.py")
    sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [STRUCTURAL, 0.10]: Trigger includes Callable[..., Dependency]
#
# The Trigger type must accept any callable returning Dependency.
###############################################################################
echo ""
echo "TEST 5: [structural] Trigger type includes Callable[..., Dependency]"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/events.py") as f:
    source = f.read()

# Find the line defining Trigger
trigger_def = None
for line in source.splitlines():
    stripped = line.strip()
    if stripped.startswith('Trigger') and '=' in stripped:
        trigger_def = stripped
        break

if trigger_def is None:
    print("FAIL: Trigger definition not found")
    sys.exit(1)

# Check that it references Callable and Dependency
if 'Callable' in trigger_def and 'Dependency' in trigger_def:
    print(f"PASS: Trigger includes Callable[..., Dependency]: {trigger_def}")
    sys.exit(0)
else:
    print(f"FAIL: Trigger does not include Callable[..., Dependency]: {trigger_def}")
    sys.exit(1)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [ANTI-STUB, 0.05]: Files not replaced with stubs
###############################################################################
echo ""
echo "TEST 6: [anti-stub] files are not stubs"
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
T6=$?
echo "  -> exit code: $T6"


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit 429a9fad5207fb27648d860a4802ff52a5b38746
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/events.py /workspace/gradio/gradio/renderable.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T7=0; echo "TEST 7: config ruff format PASS"; else T7=1; echo "TEST 7: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.25 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.20 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: Trigger type alias)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 2 (fail-to-pass: gr.on uses Trigger)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: gr.render uses Trigger) = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 4 (pass-to-pass: EventListenerCallable)  = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (structural: Callable[..., Dependency]) = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (anti-stub)                             = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 7 (config: ruff format)                   = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
