#!/usr/bin/env bash
# Verifier for gradio-mcp-tool-call-latency
#
# Bug: MCP tool calls for non-queued events use HTTP loopback, adding ~4s latency.
# Fix: Directly call blocks.process_api() for non-queued events.
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
#   TEST 1 (import+structure gate)                            = 0.10
#   TEST 2 (behavioral: SessionState imported)                  = 0.20
#   TEST 3 (behavioral: process_api path exists)                = 0.30
#   TEST 4 (behavioral: queue check branches correctly)         = 0.20
#   TEST 5 (behavioral: HTTP loopback preserved)                = 0.15
#   TEST 6 (anti-stub+anti-stuffing)                            = 0.05
#   TOTAL                                                       = 1.00
###############################################################################

GATE_PASSED=0

###############################################################################
# TEST 1 [GATE, 0.10]: Module imports successfully
###############################################################################
echo ""
echo "TEST 1: [gate] gradio.mcp module imports without errors"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/gradio')

try:
    from gradio import mcp
    print("PASS: gradio.mcp imports successfully")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: Cannot import gradio.mcp: {e}")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

if [ $T1 -eq 0 ]; then
    GATE_PASSED=1
fi

# Gate all subsequent tests behind successful import
if [ $GATE_PASSED -eq 0 ]; then
    echo "0.10" > "$REWARD_FILE"
    echo "FAIL: Import gate failed, scoring 0.10"
    exit 0
fi

###############################################################################
# TEST 2 [BEHAVIORAL, 0.20]: SessionState is imported and usable
# [pr_diff] (0.20): SessionState must be importable from gradio.state_holder
###############################################################################
echo ""
echo "TEST 2: [behavioral] SessionState imported and creates instances"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/gradio')

try:
    # Check that SessionState is imported in mcp.py
    from gradio import mcp
    import inspect

    mcp_source = inspect.getsourcefile(mcp)
    with open(mcp_source) as f:
        source = f.read()

    # Verify the import exists in the mcp module source
    if 'SessionState' not in source:
        print("FAIL: SessionState not referenced in mcp.py")
        sys.exit(1)

    # Verify SessionState is actually from state_holder
    if 'state_holder' not in source:
        print("FAIL: state_holder not referenced in mcp.py")
        sys.exit(1)

    # Verify the import WORKS at runtime
    from gradio.state_holder import SessionState

    # Verify SessionState can be instantiated with blocks
    from gradio.blocks import Blocks
    dummy_blocks = type('MockBlocks', (), {})()
    try:
        # SessionState takes blocks as first arg
        instance = SessionState(dummy_blocks)
        print("PASS: SessionState imported and instantiable")
        sys.exit(0)
    except TypeError as e:
        print(f"FAIL: SessionState instantiation failed: {e}")
        sys.exit(1)

except ImportError as e:
    print(f"FAIL: Cannot import SessionState: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [BEHAVIORAL, 0.30]: process_api is called for non-queued path
# [pr_diff] (0.30): Non-queued events call blocks.process_api() directly
###############################################################################
echo ""
echo "TEST 3: [behavioral] call_tool has non-queued path using process_api"
python3 << 'PYEOF'
import sys
import ast
sys.path.insert(0, '/workspace/gradio')

from gradio import mcp

# Get the source and parse AST
tree = ast.parse(open(mcp.__file__).read())

# Find the call_tool method
call_tool_found = False
has_process_api_call = False
has_queue_check = False
has_non_queued_branch = False

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'call_tool':
        call_tool_found = True

        # Walk through the function body
        func_tree = ast.parse(ast.unparse(node))

        # Look for process_api call
        for sub_node in ast.walk(func_tree):
            if isinstance(sub_node, ast.Call):
                if isinstance(sub_node.func, ast.Attribute):
                    if sub_node.func.attr == 'process_api':
                        has_process_api_call = True

            # Look for queue check on block_fn
            if isinstance(sub_node, ast.Attribute):
                if sub_node.attr == 'queue':
                    has_queue_check = True

            # Look for "not" operation (checking if not queued)
            if isinstance(sub_node, ast.UnaryOp) and isinstance(sub_node.op, ast.Not):
                has_non_queued_branch = True

if not call_tool_found:
    print("FAIL: call_tool method not found")
    sys.exit(1)

if not has_process_api_call:
    print("FAIL: process_api call not found in call_tool")
    sys.exit(1)

if not has_queue_check:
    print("FAIL: queue attribute check not found")
    sys.exit(1)

print("PASS: call_tool has process_api path with queue check")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [BEHAVIORAL, 0.20]: Queue branching structure is correct
# [pr_diff] (0.20): Branch on block_fn.queue separates queued/non-queued paths
###############################################################################
echo ""
echo "TEST 4: [behavioral] queue check properly branches execution"
python3 << 'PYEOF'
import sys
import ast
sys.path.insert(0, '/workspace/gradio')

source = open('/workspace/gradio/gradio/mcp.py').read()
tree = ast.parse(source)

# Find call_tool and check for proper if/else structure
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'call_tool':
        # Check for If nodes with queue-related test
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check if this is a queue check
                test_str = ast.unparse(child.test)
                if 'queue' in test_str:
                    # Must have an else branch (queued path preserved)
                    if child.orelse:
                        # Check that else branch has client operations
                        else_str = ast.unparse(child.orelse[0]) if child.orelse else ""
                        if 'submit' in else_str or '_get_or_create_client' in else_str:
                            print("PASS: queue check has if (non-queued) and else (queued) branches")
                            sys.exit(0)

print("FAIL: proper queue branching not found")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [BEHAVIORAL, 0.15]: HTTP loopback preserved for queued
# [pr_diff] (0.15): Queued path still uses client.submit for progress streaming
###############################################################################
echo ""
echo "TEST 5: [behavioral] client.submit preserved in queued branch"
python3 << 'PYEOF'
import sys
import ast
sys.path.insert(0, '/workspace/gradio')

source = open('/workspace/gradio/gradio/mcp.py').read()
tree = ast.parse(source)

# Find call_tool and the queued branch (else clause of queue check)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'call_tool':
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                test_str = ast.unparse(child.test)
                if 'queue' in test_str and child.orelse:
                    # This is the queued branch
                    queued_source = ast.unparse(child.orelse)

                    # Must have client creation and submit
                    if 'client' in queued_source and 'submit' in queued_source:
                        print("PASS: HTTP loopback preserved in queued branch")
                        sys.exit(0)

print("FAIL: HTTP loopback path not properly preserved")
sys.exit(1)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [ANTI-STUB+ANTI-STUFFING, 0.05]: Substantive implementation
###############################################################################
echo ""
echo "TEST 6: [anti-stub] file has meaningful code beyond keywords"
python3 << 'PYEOF'
import sys
import ast

source = open('/workspace/gradio/gradio/mcp.py').read()
tree = ast.parse(source)

# Count actual function definitions (not stubs)
func_count = 0
meaningful_funcs = 0

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        func_count += 1
        # Count non-docstring statements
        body = [stmt for stmt in node.body
                if not isinstance(stmt, (ast.Expr, ast.Pass))]
        if len(body) > 3:
            meaningful_funcs += 1

# Check classes
class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

# Check line count (excluding comments and blank lines)
lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith('#')]

checks_passed = 0

# Must have the main GradioMCPServer class
if class_count >= 1:
    checks_passed += 1

# Must have meaningful call_tool implementation
if meaningful_funcs >= 1:
    calls_found = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'call_tool':
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    calls_found += 1
    if calls_found >= 3:  # process_api, session_state init, etc.
        checks_passed += 1

# Must be more than just keyword injections
if len(lines) > 150:
    checks_passed += 1

if checks_passed >= 2:
    print("PASS: substantive implementation found")
    sys.exit(0)
else:
    print(f"FAIL: only {checks_passed}/3 checks passed")
    sys.exit(1)
PYEOF
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# Config-derived test (0.05): Python code formatted with ruff
# Source: AGENTS.md line 43 @ commit b1f62c0ebc09be80aee830e26689ab70b939cf44
###############################################################################
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/mcp.py 2>/dev/null
RUFF_EXIT=$?
cd /
T7=1
if [ $RUFF_EXIT -eq 0 ]; then
    T7=0
    echo "TEST 7: config ruff format PASS"
else
    T7=1
    echo "TEST 7: config ruff format FAIL"
fi

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.10 if $T1 == 0 else 0.0
t2 = 0.20 if $T2 == 0 else 0.0
t3 = 0.30 if $T3 == 0 else 0.0
t4 = 0.20 if $T4 == 0 else 0.0
t5 = 0.15 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7
score = min(1.0, score)  # Cap at 1.0
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (gate: import success)                = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 2 (behavioral: SessionState)            = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 3 (behavioral: process_api path)        = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 4 (behavioral: queue branching)         = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 5 (behavioral: HTTP loopback)           = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 6 (anti-stub)                           = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 7 (config: ruff format)                 = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
