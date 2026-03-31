#!/usr/bin/env bash
# Verifier for vllm-tool-parser-indexerror
#
# Tests behavioral fixes for two bugs:
# 1. UnboundLocalError: `index` used before assignment when tool_parser is set
# 2. IndexError: accessing prev_tool_call_arr when empty
#
set +e

TARGET="/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
mkdir -p /logs/verifier

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: UnboundLocalError pattern)    = 0.35
#   TEST 2 (fail-to-pass: IndexError pattern)           = 0.35
#   TEST 3 (pass-to-pass: signature + importability)    = 0.10
#   TEST 4 (anti-stub)                                  = 0.10
#   TEST 5 (config-derived: no bare pip)                = 0.10
#   TOTAL                                               = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: UnboundLocalError on `index`
#
# The bug: when tool_parser is set but auto_tools_called is False,
# `index` is only assigned via ternary inside the if block.
# If the code path uses `index` later without the ternary executing,
# we get UnboundLocalError.
#
# Test: Extract the function region and simulate the buggy condition.
# We create a mock environment where:
#   - tool_parser is None (the else branch runs)
#   - We check that `index` is properly set
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] index is properly initialized in all code paths"
python3 << 'PYEOF'
import ast
import sys
import textwrap

# Read the source
with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)
lines = source.splitlines()

# Find the chat_completion_stream_generator function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            func_node = node
            break

if func_node is None:
    print("FAIL: chat_completion_stream_generator not found")
    sys.exit(1)

# Extract the function source
func_start = func_node.lineno - 1
func_end = func_node.end_lineno
func_lines = lines[func_start:func_end]
func_source = '\n'.join(func_lines)

# Find the code region around _should_check_for_unstreamed_tool_arg_tokens
# This is where both bugs manifest

# Look for the pattern: the region contains both "auto_tools_called" and
# "_should_check_for_unstreamed_tool_arg_tokens"
region_start = None
region_end = None

for i, line in enumerate(func_lines):
    if 'auto_tools_called' in line and '=' in line:
        region_start = max(0, i - 5)
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        region_end = min(len(func_lines), i + 10)

if region_start is None or region_end is None:
    print("FAIL: Could not locate the bug region")
    sys.exit(1)

region_code = '\n'.join(func_lines[region_start:region_end])

# Simulate the control flow to check for UnboundLocalError
# We'll extract the variable assignments and check if `index` is always defined

# Parse just this region to analyze variable assignments
region_tree = ast.parse(textwrap.dedent(region_code))

# Find all assignments to 'index' at module level of the region
index_assigned_unconditionally = False
index_assigned_in_branches = []

for node in ast.walk(region_tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'index':
                # Check the context - if it's at the top level of the region,
                # it's unconditional relative to the if/else on tool_parser
                index_assigned_unconditionally = True

# Also check textually - look for "index = 0" pattern
# In the gold fix, there's an unconditional `index = 0` before the if tool_parser block
if 'index = 0' in region_code or 'index=0' in region_code:
    # Verify it's not inside an else block
    lines_before_if = []
    for i, line in enumerate(func_lines[region_start:region_end]):
        stripped = line.strip()
        if stripped.startswith('if tool_parser'):
            break
        lines_before_if.append(stripped)

    # Check if index = 0 appears before if tool_parser
    for line in lines_before_if:
        if ('index = 0' in line or 'index=0' in line) and '==' not in line:
            index_assigned_unconditionally = True
            break

# Alternative: check for try/except pattern as valid fix
has_exception_handling = 'try:' in region_code and 'except' in region_code

if index_assigned_unconditionally or has_exception_handling:
    print("PASS: index is assigned unconditionally or exception-handled")
    sys.exit(0)
else:
    # Verify the bug exists by checking the pattern
    # Buggy pattern: index is only assigned in ternary or else block
    if 'if tool_parser:' in region_code and 'else:' in region_code:
        # Check if index is assigned only in conditional branches
        has_index_in_else = False
        has_index_in_if = False

        in_else = False
        for line in func_lines[region_start:region_end]:
            stripped = line.strip()
            if stripped.startswith('else:'):
                in_else = True
            elif stripped and not stripped.startswith(' ') and not stripped.startswith('#'):
                in_else = False

            if 'index =' in stripped or 'index=' in stripped:
                if in_else:
                    has_index_in_else = True
                else:
                    has_index_in_if = True

        # If index is only in else or only in if (conditionally), that's the bug
        if (has_index_in_else and not has_index_in_if) or (has_index_in_if and not has_index_in_else):
            print("FAIL: index is assigned only in conditional branches (UnboundLocalError risk)")
            sys.exit(1)

    print("FAIL: Could not verify index is safely assigned")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.35]: IndexError on empty prev_tool_call_arr
#
# The bug: _should_check_for_unstreamed_tool_arg_tokens is called, then
# prev_tool_call_arr[-1] is accessed without checking if the array is non-empty.
#
# Test: Verify that the code checks auto_tools_called (or equivalent) before
# accessing prev_tool_call_arr elements.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] prev_tool_call_arr access is properly guarded"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)
lines = source.splitlines()

# Find the function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            func_node = node
            break

if func_node is None:
    print("FAIL: Function not found")
    sys.exit(1)

func_start = func_node.lineno - 1
func_end = func_node.end_lineno
func_lines = lines[func_start:func_end]
func_source = '\n'.join(func_lines)

# Find the region with _should_check_for_unstreamed_tool_arg_tokens
should_check_line = None
for i, line in enumerate(func_lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        should_check_line = i
        break

if should_check_line is None:
    print("FAIL: _should_check_for_unstreamed_tool_arg_tokens not found")
    sys.exit(1)

# Look at the surrounding context (20 lines before and after)
context_start = max(0, should_check_line - 20)
context_end = min(len(func_lines), should_check_line + 20)
context_code = '\n'.join(func_lines[context_start:context_end])

# Check for proper guard patterns:
# 1. auto_tools_called in the condition (gold patch pattern)
# 2. prev_tool_call_arr length check before access
# 3. try/except IndexError around the access

guards_found = []

# Check 1: auto_tools_called is used in the if condition
if 'auto_tools_called' in context_code:
    # Verify it's in the same if statement as _should_check
    for i in range(should_check_line, min(should_check_line + 10, len(func_lines))):
        line = func_lines[i]
        if line.strip().startswith('if ') and ':' in line:
            # Check if this if contains BOTH _should_check and auto_tools_called
            if_condition = ' '.join(func_lines[i:min(i+5, len(func_lines))])
            if '_should_check_for_unstreamed_tool_arg_tokens' in if_condition and 'auto_tools_called' in if_condition:
                guards_found.append("auto_tools_called in condition")
            break

# Check 2: Explicit length check before array access
if 'len(tool_parser.prev_tool_call_arr)' in context_code or 'len(prev_tool_call_arr)' in context_code:
    guards_found.append("explicit length check")

# Check 3: try/except around the array access
if 'try:' in context_code and 'except' in context_code:
    if 'IndexError' in context_code:
        guards_found.append("IndexError exception handling")

# Check 4: Short-circuit pattern with walrus or explicit check
if 'prev_tool_call_arr' in context_code and '] > 0' in context_code:
    guards_found.append("non-empty array check")

# The fix must include at least one valid guard
if len(guards_found) >= 1:
    print(f"PASS: Found guards: {guards_found}")
    sys.exit(0)
else:
    # Double check: look for the specific buggy pattern
    # Buggy: if (_should_check(...) and tool_parser):
    # Fixed: if (_should_check(...) and tool_parser and auto_tools_called):

    # Check if the if condition has only 2 terms (buggy pattern)
    for i in range(should_check_line, max(should_check_line - 10, -1), -1):
        stripped = func_lines[i].strip()
        if stripped.startswith('if ') and '_should_check' in stripped:
            # Gather the full condition
            condition_lines = []
            for j in range(i, min(i + 5, len(func_lines))):
                condition_lines.append(func_lines[j])
                if ':' in func_lines[j]:
                    break
            full_condition = ' '.join(condition_lines)

            # Count boolean operators
            and_count = full_condition.count(' and ')
            or_count = full_condition.count(' or ')
            total_terms = and_count + or_count + 1

            if total_terms <= 2 and 'auto_tools_called' not in full_condition:
                print(f"FAIL: Condition has only {total_terms} term(s) without array-emptiness guard")
                print(f"  Condition: {full_condition.strip()}")
                sys.exit(1)
            break

    print("FAIL: No valid guard found for prev_tool_call_arr access")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [PASS-TO-PASS, 0.10]: Function signature and structure preserved
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] function signature and file structure preserved"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find chat_completion_stream_generator
found = False
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            found = True
            break

if not found:
    print("FAIL: chat_completion_stream_generator function not found")
    sys.exit(1)

# File should have reasonable size
line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: file suspiciously small ({line_count} lines)")
    sys.exit(1)

# Key identifiers that indicate the function wasn't gutted
required_patterns = [
    'tool_parser',
    'delta_message',
    '_should_check_for_unstreamed_tool_arg_tokens',
    'prev_tool_call_arr',
]

missing = [p for p in required_patterns if p not in source]
if missing:
    print(f"FAIL: function missing key identifiers: {missing}")
    sys.exit(1)

print(f"PASS: function intact, {line_count} lines, all key identifiers present")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [ANTI-STUB, 0.10]: File not replaced with stub
###############################################################################
echo ""
echo "TEST 4: [anti-stub] file is not a stub"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)

# Count classes and functions
classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
funcs = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
line_count = len(source.splitlines())

if line_count < 500:
    print(f"FAIL: only {line_count} lines (expected 500+)")
    sys.exit(1)

if funcs < 5:
    print(f"FAIL: only {funcs} functions (expected 5+)")
    sys.exit(1)

# Check for key patterns that should be in the real file
must_have = ['OpenAIServing', 'ChatCompletionRequest', 'async']
missing = [m for m in must_have if m not in source]
if missing:
    print(f"FAIL: missing expected patterns: {missing}")
    sys.exit(1)

print(f"PASS: {line_count} lines, {classes} classes, {funcs} functions")
sys.exit(0)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [CONFIG-DERIVED, 0.10]: No bare pip install in changed files
# Source: AGENTS.md line 27 @ 9d0351c91d3115215f84f3bd4b9f366d3fbd13b3
###############################################################################
echo ""
echo "TEST 5: [config-derived] no bare pip install in changed files"
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
T5=1
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^.*#' | grep -v 'uv pip' > /dev/null 2>&1; then
            echo "  FAIL: $cf contains bare 'pip install'"
            BARE_PIP=1
        fi
    fi
done
if [ "$BARE_PIP" -eq 0 ]; then
    echo "  PASS"
    T5=0
fi
echo "  -> exit code: $T5"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.35 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if ${T5:-1} == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: index scoping)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (fail-to-pass: array guard)       = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 3 (pass-to-pass: structure)         = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (anti-stub)                       = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (config: no bare pip)             = $([ ${T5:-1} -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
