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

# Make gradio available for import
export PYTHONPATH="/workspace/gradio:$PYTHONPATH"

###############################################################################
# Weight allocation:
#   TEST 1 (gate: imports)                                            = GATE
#   TEST 2 (fail-to-pass: example_select not in stop events via AST)  = 0.35
#   TEST 3 (fail-to-pass: submit_btn chain via AST)                   = 0.35
#   TEST 4 (fail-to-pass: conditional events_to_cancel)               = 0.15
#   TEST 5 (pass-to-pass: ChatInterface inits without error)          = 0.10
#   TEST 6 (anti-stub: substantial implementation)                    = 0.05
#   TOTAL                                                             = 1.00
###############################################################################

###############################################################################
# GATE: Module imports successfully (syntax + basic structure)
###############################################################################
echo "GATE: Testing module import..."
python3 << 'PYEOF'
import ast
import sys

try:
    # Parse the file first
    with open("/workspace/gradio/gradio/chat_interface.py") as f:
        source = f.read()
    tree = ast.parse(source)

    # Verify ChatInterface class exists
    chat_interface = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
            chat_interface = node
            break

    if chat_interface is None:
        print("GATE FAIL: ChatInterface class not found")
        sys.exit(1)

    # Verify _setup_events method exists
    setup_events = None
    for item in chat_interface.body:
        if isinstance(item, ast.FunctionDef) and item.name == "_setup_events":
            setup_events = item
            break

    if setup_events is None:
        print("GATE FAIL: _setup_events method not found")
        sys.exit(1)

    print("GATE PASSED: Valid Python with ChatInterface._setup_events")
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: Syntax error - {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: _setup_stop_events event_triggers excludes example_select
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] example_select removed from _setup_stop_events triggers"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ChatInterface class
chat_interface = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
        chat_interface = node
        break

# Find _setup_events method
setup_events = None
for item in chat_interface.body:
    if isinstance(item, ast.FunctionDef) and item.name == "_setup_events":
        setup_events = item
        break

# Find _setup_stop_events call and analyze its event_triggers keyword
stop_events_call = None

class StopEventsFinder(ast.NodeVisitor):
    def __init__(self):
        self.found = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "_setup_stop_events":
            self.found = node
        elif isinstance(node.func, ast.Name) and node.func.id == "_setup_stop_events":
            self.found = node
        self.generic_visit(node)

finder = StopEventsFinder()
finder.visit(setup_events)
stop_events_call = finder.found

if stop_events_call is None:
    print("FAIL: _setup_stop_events call not found")
    sys.exit(1)

# Check event_triggers keyword argument
has_example_select = False
for kw in stop_events_call.keywords:
    if kw.arg == "event_triggers":
        # event_triggers should be a list without example_select
        if isinstance(kw.value, ast.List):
            for elt in kw.value.elts:
                # Check for any reference to example_select
                if isinstance(elt, ast.Attribute) and "example_select" in elt.attr:
                    has_example_select = True
                    break
                # Check for variable names containing example_select
                if isinstance(elt, ast.Name) and "example_select" in elt.id:
                    has_example_select = True
                    break
                # Check for subscript with example_select
                if isinstance(elt, ast.Subscript):
                    elt_str = ast.dump(elt)
                    if "example_select" in elt_str:
                        has_example_select = True
                        break
        break

if has_example_select:
    print("FAIL: example_select still in event_triggers for _setup_stop_events")
    sys.exit(1)

print("PASS: example_select removed from _setup_stop_events event_triggers")
sys.exit(0)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.35]: submit_btn=False added in .then() chain
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] submit_btn=False added as .then() step in example chain"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ChatInterface class and _setup_events
chat_interface = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
        chat_interface = node
        break

setup_events = None
for item in chat_interface.body:
    if isinstance(item, ast.FunctionDef) and item.name == "_setup_events":
        setup_events = item
        break

# Look for pattern: some_event = some_event.then(... submit_btn=False ...)
# This is a chained assignment pattern

class ThenChainFinder(ast.NodeVisitor):
    def __init__(self):
        self.has_submit_btn_false_in_then = False

    def visit_Assign(self, node):
        # Look for: X = X.then(...)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            if isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute) and call.func.attr == "then":
                    # Check if any argument has submit_btn=False
                    for kw in call.keywords:
                        if kw.arg == "api_name":
                            continue  # Skip api_name, look at actual args
                    # Check the function call arguments for submit_btn=False
                    for kw in call.keywords:
                        # Look for fn keyword containing lambda/function with submit_btn=False
                        if kw.arg == "fn":
                            fn_str = ast.dump(kw.value)
                            if "submit_btn" in fn_str and "False" in fn_str:
                                self.has_submit_btn_false_in_then = True
                                break
                    # Also check positional args for the function
                    for arg in call.args:
                        arg_str = ast.dump(arg)
                        if "submit_btn" in arg_str and "False" in arg_str:
                            self.has_submit_btn_false_in_then = True
                            break
        self.generic_visit(node)

    def visit_Keyword(self, node):
        # Direct check for submit_btn=False in keywords
        if node.arg == "submit_btn":
            if isinstance(node.value, ast.Constant) and node.value.value == False:
                self.has_submit_btn_false_in_then = True
        self.generic_visit(node)

finder = ThenChainFinder()
finder.visit(setup_events)

if not finder.has_submit_btn_false_in_then:
    # Fallback: check if there's a .then() call that affects textbox submit_btn
    source_str = ast.dump(setup_events)
    # Look for pattern: .then() with submit_btn and False in the vicinity
    if ".then(" not in source_str:
        print("FAIL: No .then() calls found in _setup_events")
        sys.exit(1)

    # More robust: look for the pattern in the actual source
    lines = source.split('\n')
    in_setup_events = False
    setup_events_start = setup_events.lineno - 1
    setup_events_end = setup_events.end_lineno

    event_section = '\n'.join(lines[setup_events_start:setup_events_end])

    # Check for submit_btn=False in a .then() context related to examples
    if "submit_btn" in event_section and "False" in event_section and ".then(" in event_section:
        # Verify it's in example-related code section
        if "example" in event_section.lower():
            print("PASS: submit_btn=False found in example-related .then() chain")
            sys.exit(0)

    print("FAIL: submit_btn=False in .then() chain not found")
    sys.exit(1)

print("PASS: submit_btn=False found in .then() chain")
sys.exit(0)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: Conditional events_to_cancel with example flag
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] Conditional inclusion of example_select_event in events_to_cancel"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ChatInterface class and _setup_events
chat_interface = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
        chat_interface = node
        break

setup_events = None
for item in chat_interface.body:
    if isinstance(item, ast.FunctionDef) and item.name == "_setup_events":
        setup_events = item
        break

# Look for conditional appending of example_select_event to events_to_cancel
# Pattern should be: if example_select_event is not None AND some_flag:
#   events_to_cancel.append(example_select_event)

source_str = ast.dump(setup_events)

# Check for the pattern in source text (more reliable for this complex check)
lines = source.split('\n')
setup_events_start = setup_events.lineno - 1
setup_events_end = setup_events.end_lineno
event_section = '\n'.join(lines[setup_events_start:setup_events_end])

# Must have conditional check involving example_select_event and events_to_cancel
has_conditional = False
has_example_event_in_cancel = False

class ConditionalChecker(ast.NodeVisitor):
    def __init__(self):
        self.has_conditional_append = False
        self.flag_variable = None

    def visit_If(self, node):
        # Check for: if X is not None and Y:
        cond_str = ast.dump(node.test)
        if "example_select" in cond_str and ("is not None" in cond_str or "Not" in cond_str):
            # Check if body appends to events_to_cancel
            for stmt in node.body:
                stmt_str = ast.dump(stmt)
                if "events_to_cancel" in stmt_str and ("append" in stmt_str or "example_select" in stmt_str):
                    self.has_conditional_append = True
                    # Try to extract flag variable
                    if isinstance(node.test, ast.BoolOp):
                        for value in node.test.values:
                            if isinstance(value, ast.Name) and value.id != "example_select_event":
                                self.flag_variable = value.id
                    break
        self.generic_visit(node)

checker = ConditionalChecker()
checker.visit(setup_events)

# Alternative: check for flag variable definition used in conditional
has_flag_variable = False
flag_names = ["example_select_runs", "should_run_examples", "example_stops_events"]

class FlagFinder(ast.NodeVisitor):
    def __init__(self):
        self.found_flag = False

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id in flag_names or "runs" in target.id or "example" in target.id.lower():
                    self.found_flag = True
        self.generic_visit(node)

flag_finder = FlagFinder()
flag_finder.visit(setup_events)

if checker.has_conditional_append:
    print("PASS: Conditional inclusion of example event in events_to_cancel")
    sys.exit(0)

if flag_finder.found_flag and "events_to_cancel" in event_section and "example_select" in event_section:
    # Check for any conditional involving events_to_cancel
    if "if" in event_section and "example_select" in event_section.lower():
        print("PASS: Conditional example event logic found")
        sys.exit(0)

# Fallback: check for the original bug pattern (direct append without condition)
# If we see: events_to_cancel.append(example_select_event) directly in the code (not in if block)
# with only 'is not None' check, that's the buggy version
lines = event_section.split('\n')
for i, line in enumerate(lines):
    if "events_to_cancel" in line and "append" in line and "example_select" in line:
        # Check if this is inside an if block with additional conditions
        # Look backwards for the if statement
        for j in range(i-1, -1, -1):
            if lines[j].strip().startswith("if "):
                if_str = lines[j].lower()
                if "is not None" in if_str and "and" not in if_str:
                    print("FAIL: example_select_event added unconditionally (only None check)")
                    sys.exit(1)
                else:
                    print("PASS: Conditional logic found for events_to_cancel")
                    sys.exit(0)

print("FAIL: Conditional events_to_cancel logic not found")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: Module imports ChatInterface without error
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] ChatInterface imports and instantiates correctly"
python3 << 'PYEOF'
import sys
import os
os.chdir("/workspace/gradio")

try:
    from gradio.chat_interface import ChatInterface

    # Verify it's a class
    if not isinstance(ChatInterface, type):
        print("FAIL: ChatInterface is not a class")
        sys.exit(1)

    # Verify it has _setup_events method
    if not hasattr(ChatInterface, "_setup_events"):
        print("FAIL: _setup_events method not found")
        sys.exit(1)

    print("PASS: ChatInterface imports and has required methods")
    sys.exit(0)
except ImportError as e:
    print(f"FAIL: Import error - {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Error importing - {e}")
    sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.05]: Substantial implementation
###############################################################################
echo ""
echo "TEST 5: [anti-stub] ChatInterface has substantial implementation"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ChatInterface class
chat_interface = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
        chat_interface = node
        break

if chat_interface is None:
    print("FAIL: ChatInterface not found")
    sys.exit(1)

# Count methods
methods = [item for item in chat_interface.body if isinstance(item, ast.FunctionDef)]
method_lines = sum(method.end_lineno - method.lineno for method in methods)

# Count significant methods (non-trivial)
significant_methods = 0
for method in methods:
    body = method.body
    # Count non-pass, non-docstring statements
    stmt_count = 0
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue  # Docstring
        stmt_count += 1
    if stmt_count > 3:
        significant_methods += 1

if len(methods) < 5 or significant_methods < 3 or method_lines < 100:
    print(f"FAIL: Only {len(methods)} methods, {significant_methods} significant, ~{method_lines} method lines")
    sys.exit(1)

print(f"PASS: {len(methods)} methods, {significant_methods} significant, ~{method_lines} lines")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.35 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.05 if $T5 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: example_select removed)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (fail-to-pass: submit_btn=False chain)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 3 (fail-to-pass: conditional events_to_cancel) = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: module imports)             = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub)                                = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
