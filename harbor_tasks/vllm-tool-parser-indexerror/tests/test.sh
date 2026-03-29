#!/usr/bin/env bash
# Verifier for vllm-tool-parser-indexerror
#
# Design philosophy (post-OpenAI SWE-bench critique):
#   - PRIMARY: fail-to-pass behavioral tests that are implementation-agnostic
#   - SECONDARY: structural checks as partial-credit supplementary signal
#   - REGRESSION: pass-to-pass test ensuring existing logic isn't broken
#
# The bug: in chat_completion_stream_generator(), `index` can be referenced
# before assignment when tool_parser is None, and the code checks for
# unstreamed tool arg tokens even when no tool calls were detected, causing
# IndexError on empty prev_tool_call_arr.
#
# A correct fix must satisfy:
#   1. `index` is always defined (no UnboundLocalError path)
#   2. Accessing prev_tool_call_arr[-1] only happens when array is non-empty
#
# We do NOT require:
#   - A specific variable name like `should_check`
#   - A specific restructuring order
#   - Use of `auto_tools_called` (any equivalent guard is fine)
#
set +e

TARGET="/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
PASS=0
TOTAL=5

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
# TEST 1 [FAIL-TO-PASS / behavioral]: index is always defined
#   Extract the relevant code region and execute it with tool_parser=None.
#   Buggy code: UnboundLocalError on `index` in the else-less path.
#   Fixed code: `index` is always assigned, no error.
###############################################################################
echo ""
echo "TEST 1/5: [fail-to-pass] index is always defined when tool_parser is None"
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

lines = source.split('\n')

# Find the block containing the index/auto_tools_called logic.
# We look for the region around "auto_tools_called" and extract ~30 lines.
region_start = None
for i, line in enumerate(lines):
    if 'auto_tools_called' in line and '=' in line and 'False' in line:
        # Back up a few lines to capture any pre-block assignments
        region_start = max(0, i - 5)
        break

if region_start is None:
    # If auto_tools_called pattern is gone, the fix may have restructured
    # differently. Look for _should_check_for_unstreamed_tool_arg_tokens instead.
    for i, line in enumerate(lines):
        if '_should_check_for_unstreamed_tool_arg_tokens' in line:
            region_start = max(0, i - 10)
            break

if region_start is None:
    print("FAIL: could not locate the relevant code region")
    sys.exit(1)

# Extract ~40 lines of the region
region_end = min(len(lines), region_start + 40)
region = '\n'.join(lines[region_start:region_end])

# De-indent to make it executable
region_dedented = textwrap.dedent(region)

# Create a mock environment that simulates tool_parser=None
test_code = '''
class MockOutput:
    text = "hello"
    token_ids = [1, 2, 3]

class MockDeltaMessage:
    tool_calls = None
    content = "test"

class MockSelf:
    def _should_check_for_unstreamed_tool_arg_tokens(self, delta_message, output):
        return True

self = MockSelf()
tool_parser = None
delta_message = MockDeltaMessage()
output = MockOutput()

# Execute the extracted region. If `index` is referenced before assignment,
# this will raise UnboundLocalError.
try:
    exec(REGION_CODE, {
        'self': self,
        'tool_parser': tool_parser,
        'delta_message': delta_message,
        'output': output,
        'len': len,
        'isinstance': isinstance,
    })
    # If we get here without error, index should be defined
    print("PASS: code executed without UnboundLocalError")
except UnboundLocalError as e:
    if 'index' in str(e):
        print(f"FAIL: UnboundLocalError: {e}")
        raise
    # Other UnboundLocalErrors from our incomplete mock env are OK
    print(f"PASS: no index UnboundLocalError (got unrelated: {e})")
except NameError as e:
    if 'index' in str(e):
        print(f"FAIL: NameError on index: {e}")
        raise
    print(f"PASS: no index error (got unrelated NameError: {e})")
except Exception as e:
    # Other exceptions (AttributeError on mock objects etc.) are expected
    # since we're only testing a code fragment. The key check is no
    # UnboundLocalError/NameError on `index`.
    print(f"PASS: no index error (got expected mock error: {type(e).__name__})")
'''

try:
    exec(test_code, {'REGION_CODE': region_dedented})
except (UnboundLocalError, NameError) as e:
    if 'index' in str(e):
        print(f"FAIL: {e}")
        sys.exit(1)
except Exception:
    pass  # Mock-related errors are fine

# If we haven't exited with 1, the test passes
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# TEST 2 [FAIL-TO-PASS / behavioral]: empty tool_call_arr doesn't IndexError
#   With tool_parser having an empty prev_tool_call_arr, the unstreamed-token
#   check path should not try to index into the empty array.
###############################################################################
echo ""
echo "TEST 2/5: [fail-to-pass] empty prev_tool_call_arr doesn't cause IndexError"
python3 << 'PYEOF'
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

lines = source.split('\n')

# The core bug: when tool_parser exists but prev_tool_call_arr is empty,
# the code could try `prev_tool_call_arr[-1]` or `len(...) - 1` on empty list.
# Find the region and check if there's a guard.

# Strategy: look for any access to prev_tool_call_arr that could IndexError
# when the array is empty. Check if it's guarded by a length/emptiness check.

# Find all references to prev_tool_call_arr
risky_accesses = []
for i, line in enumerate(lines):
    stripped = line.strip()
    # Look for indexing into prev_tool_call_arr or len()-1 patterns
    if 'prev_tool_call_arr' in stripped:
        # Check if this is inside a conditional that guards for non-empty
        # Look at surrounding context for guard
        context_before = '\n'.join(lines[max(0, i-10):i])
        has_guard = False
        # Accept any of: len() > 0, bool check, auto_tools_called, not empty, etc.
        if any(g in context_before for g in [
            'auto_tools_called',
            'len(tool_parser.prev_tool_call_arr) > 0',
            'len(tool_parser.prev_tool_call_arr) >',
            'tool_parser.prev_tool_call_arr',  # truthy check
            'if not tool_parser',
        ]):
            has_guard = True

        # Check if the line itself is the guard definition
        if 'len(tool_parser.prev_tool_call_arr)' in stripped and '>' in stripped:
            has_guard = True
        if 'auto_tools_called' in stripped and ('=' in stripped or 'if' in stripped):
            has_guard = True

        # Check if accessing with index (risky if unguarded)
        if '[' in stripped and ']' in stripped and 'prev_tool_call_arr[' in stripped:
            if not has_guard:
                risky_accesses.append((i+1, stripped))
        if 'len(tool_parser.prev_tool_call_arr) - 1' in stripped:
            if not has_guard:
                risky_accesses.append((i+1, stripped))

# Now check the critical path: _should_check_for_unstreamed_tool_arg_tokens
# In buggy code, this runs even when prev_tool_call_arr is empty.
# In fixed code, there should be an emptiness guard before the indexing block.
for i, line in enumerate(lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        # Look at the if-condition containing this call
        # Check if there's ALSO a non-empty guard in the same condition
        context = ' '.join(l.strip() for l in lines[max(0,i-3):i+8])

        # The buggy code: `if self._should_check(...) and tool_parser:`
        # - enters the block even with empty prev_tool_call_arr
        # The fixed code adds: `and auto_tools_called` or `and len(...) > 0` or similar

        has_emptiness_guard = False
        for guard in ['auto_tools_called', 'prev_tool_call_arr', 'len(', 'tool_calls']:
            if guard in context and ('and' in context or 'if' in context):
                has_emptiness_guard = True
                break

        if not has_emptiness_guard:
            print(f"FAIL: _should_check block at line {i+1} has no emptiness guard")
            print(f"  context: {context[:200]}")
            sys.exit(1)
        else:
            print(f"PASS: _should_check block has emptiness guard")
            sys.exit(0)

# If we couldn't find the pattern at all, check if risky accesses remain
if risky_accesses:
    print(f"FAIL: unguarded prev_tool_call_arr access at lines: {risky_accesses}")
    sys.exit(1)

print("PASS: no unguarded prev_tool_call_arr access found")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# TEST 3 [PASS-TO-PASS / regression]: file retains all critical streaming logic
#   These patterns must exist both before and after the fix.
###############################################################################
echo ""
echo "TEST 3/5: [pass-to-pass] streaming logic preserved"
python3 << 'PYEOF'
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

# These are structural invariants that any correct fix must preserve
required = [
    'chat_completion_stream_generator',
    'tool_parser',
    'delta_message',
    '_should_check_for_unstreamed_tool_arg_tokens',
]

missing = [p for p in required if p not in source]
if missing:
    print(f"FAIL: missing critical patterns: {missing}")
    sys.exit(1)

line_count = len(source.split('\n'))
if line_count < 500:
    print(f"FAIL: file too small ({line_count} lines)")
    sys.exit(1)

print(f"PASS: all critical patterns present, {line_count} lines")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# TEST 4 [STRUCTURAL / supplementary]: index is unconditionally initialized
#   This is a softer structural check: `index` must be assigned at an
#   indentation level that guarantees it's always defined, regardless of
#   which branch is taken. Accepts any approach that achieves this.
###############################################################################
echo ""
echo "TEST 4/5: [structural] index is always initialized (not conditional-only)"
python3 << 'PYEOF'
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

lines = source.split('\n')

# Find where `auto_tools_called` is first set in the streaming function.
# Then check that `index` has a default assignment at the same or outer scope.
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'auto_tools_called' in stripped and 'False' in stripped and '=' in stripped:
        target_indent = len(line) - len(line.lstrip())

        # Check: is there an `index =` at target_indent or less within +-10 lines?
        found_outer_init = False
        for j in range(max(0, i-10), min(len(lines), i+15)):
            l = lines[j]
            ls = l.strip()
            if 'index' in ls and '=' in ls and not ls.startswith('#') and not ls.startswith('if'):
                # Parse: is this `index = <something>` (assignment, not comparison)?
                # Simple heuristic: contains `index =` but not `== index` or `index ==`
                if ('index =' in ls or 'index=' in ls) and '==' not in ls:
                    assign_indent = len(l) - len(l.lstrip())
                    if assign_indent <= target_indent:
                        found_outer_init = True
                        break

        if found_outer_init:
            print("PASS: index has unconditional initialization")
            sys.exit(0)
        else:
            # Fallback: maybe they removed the concept of `index` entirely
            # or restructured so it's computed differently. Check if `index`
            # is used at all in the critical region.
            region = '\n'.join(lines[i:i+30])
            if 'index' not in region:
                print("PASS: index variable removed (alternative fix)")
                sys.exit(0)

            # Check if index is in a try/except that catches the error
            if 'try:' in region and ('except' in region or 'NameError' in region):
                print("PASS: index access is exception-guarded")
                sys.exit(0)

            print("FAIL: index may not be initialized on all paths")
            sys.exit(1)

print("FAIL: could not find auto_tools_called region")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# TEST 5 [STRUCTURAL / supplementary]: _should_check path is properly guarded
#   The unstreamed-token check should only run when there are actual tool calls.
#   We accept any mechanism: auto_tools_called, len() > 0, truthy check, etc.
###############################################################################
echo ""
echo "TEST 5/5: [structural] tool-arg-token check is guarded against empty state"
python3 << 'PYEOF'
import sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

lines = source.split('\n')

for i, line in enumerate(lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        # Get the full if-condition context (may span multiple lines)
        # Look backward for `if` and forward for `:`
        context_lines = lines[max(0, i-5):min(len(lines), i+8)]
        context = ' '.join(l.strip() for l in context_lines)

        # Any of these guard patterns is valid:
        guards = [
            'auto_tools_called',              # boolean flag check
            'len(tool_parser.prev_tool_call_arr)',  # length check
            'tool_parser.prev_tool_call_arr',  # truthy check on list
            'not auto_tools_called',           # inverted check (early return)
        ]

        # Also valid: the _should_check call is INSIDE a block that's already
        # guarded by one of the above.
        found_guard = False
        for g in guards:
            if g in context:
                found_guard = True
                break

        # Also check: maybe the whole block was restructured to only run
        # when tool_parser has results
        if not found_guard:
            # Check if there's an early continue/return/break before the check
            for j in range(max(0, i-8), i):
                l = lines[j].strip()
                if any(kw in l for kw in ['continue', 'return', 'break']):
                    if any(g in lines[max(0,j-3):j+1][-1] for g in ['not auto_tools_called', 'not tool_parser']):
                        found_guard = True
                        break

        if found_guard:
            print("PASS: tool-arg-token check is properly guarded")
            sys.exit(0)
        else:
            print("FAIL: no guard found for tool-arg-token check")
            sys.exit(1)

print("FAIL: _should_check_for_unstreamed_tool_arg_tokens not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Final score
###############################################################################
echo ""
SCORE=$(python3 -c "print(min($PASS / $TOTAL, 1.0))")
echo "RESULT: $PASS / $TOTAL = $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt
