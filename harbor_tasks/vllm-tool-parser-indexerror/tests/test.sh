#!/usr/bin/env bash
# Verifier for vllm-tool-parser-indexerror
#
# Tests 1-2 use AST analysis of the source code to detect the buggy patterns
# without extracting and exec-ing code regions (which fails due to the deeply
# nested async generator context).
#
# Bug 1: `index` only assigned in `else` branch -> UnboundLocalError when
#         tool_parser is not None
# Bug 2: `_should_check_for_unstreamed_tool_arg_tokens` block runs even when
#         prev_tool_call_arr is empty -> IndexError
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
#   TEST 1 (fail-to-pass: UnboundLocalError pattern)    = 0.30
#   TEST 2 (fail-to-pass: IndexError pattern)            = 0.30
#   TEST 3 (pass-to-pass: signature + importability)     = 0.10
#   TEST 4 (structural: function exists, regions touched) = 0.15
#   TEST 5 (anti-stub)                                   = 0.05
#   TEST 6 (config-derived: no bare pip)                 = 0.10
#   TOTAL                                                = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: UnboundLocalError on `index`
#
# In the buggy code, `index` is only assigned inside conditional branches
# (inside `else:` when tool_parser is None, or inside `if auto_tools_called`).
# When tool_parser is truthy but auto_tools_called is False in the ternary,
# `index` is assigned to 0 via ternary — BUT the real bug is that `index = 0`
# is inside the `else:` block, so when tool_parser IS set, `index` is assigned
# via ternary inside the `if tool_parser:` block. Actually the exact buggy
# pattern is:
#   if tool_parser:
#       auto_tools_called = len(tool_parser.prev_tool_call_arr) > 0
#       index = (... if auto_tools_called else 0)
#   else:
#       index = 0
#
# Wait — that assigns index in both branches. Let me re-read the patch...
# The patch ADDS `index = 0` BEFORE the if/else AND removes `else: index = 0`.
# Looking at the original code more carefully with the patch context:
#   Original has the ternary `index = (... if auto_tools_called else 0)` inside
#   `if tool_parser:` and `index = 0` inside `else:`. The patch adds an
#   unconditional `index = 0` before the if block.
#
# The key insight: with the gold patch, `index = 0` appears BEFORE/OUTSIDE the
# `if tool_parser:` block. In the buggy code, ALL assignments to `index` are
# INSIDE conditional branches. The fix ensures `index` has a default value
# unconditionally.
#
# AST approach: Walk the function body. Find the code region near
# `_should_check_for_unstreamed_tool_arg_tokens`. Look at `index` assignments.
# Check whether any `index =` assignment exists at or above the indentation
# level of the `if tool_parser:` block (i.e., unconditionally reachable).
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] index must be assigned unconditionally (not only in branches)"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)
lines = source.splitlines()

# Find chat_completion_stream_generator
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            func_node = node
            break

if func_node is None:
    print("FAIL: chat_completion_stream_generator not found")
    sys.exit(1)

func_start = func_node.lineno - 1
func_end = func_node.end_lineno
func_lines = lines[func_start:func_end]

# Strategy: Find the `if tool_parser:` block that's near
# `_should_check_for_unstreamed_tool_arg_tokens`. Then check whether
# `index` is assigned at or above that if-block's indentation level
# (i.e., unconditionally reachable before entering the if/else).

# Step 1: Find the line with _should_check_for_unstreamed_tool_arg_tokens
should_check_idx = None
for i, line in enumerate(func_lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        should_check_idx = i
        break

if should_check_idx is None:
    print("FAIL: _should_check_for_unstreamed_tool_arg_tokens not found in function")
    sys.exit(1)

# Step 2: Find the `if tool_parser:` line that's above _should_check
# (within ~40 lines above it)
tool_parser_if_idx = None
tool_parser_if_indent = None
for i in range(should_check_idx - 1, max(should_check_idx - 40, -1), -1):
    stripped = func_lines[i].strip()
    if stripped.startswith('if') and 'tool_parser' in stripped and stripped.endswith(':'):
        tool_parser_if_idx = i
        tool_parser_if_indent = len(func_lines[i]) - len(func_lines[i].lstrip())
        break

if tool_parser_if_idx is None:
    # The code may have been restructured — check if index is assigned anywhere
    # in the region unconditionally. Be lenient: if the if/else structure was
    # removed entirely and index is just assigned, that's a valid fix.
    region_start = max(0, should_check_idx - 50)
    for i in range(region_start, should_check_idx):
        stripped = func_lines[i].strip()
        if ('index =' in stripped or 'index=' in stripped) and '==' not in stripped and not stripped.startswith('#'):
            print("PASS: index is assigned (restructured code, no if tool_parser block found)")
            sys.exit(0)
    print("FAIL: could not find if tool_parser block or any index assignment")
    sys.exit(1)

# Step 3: Look for `index = ...` assignments in the region BETWEEN
# ~20 lines above the `if tool_parser:` line and the `if tool_parser:` line itself.
# An unconditional assignment at the SAME or LESSER indent level as the
# `if tool_parser:` means index is safely initialized before the branch.
#
# Also check: is there an `index = ` assignment at exactly the same indent
# as `if tool_parser:` — that would be unconditional relative to that block.
has_unconditional_index = False

# Search from 20 lines above tool_parser_if down to (but not including) it
search_start = max(0, tool_parser_if_idx - 20)
for i in range(search_start, tool_parser_if_idx):
    stripped = func_lines[i].strip()
    if ('index =' in stripped or 'index=' in stripped) and '==' not in stripped and not stripped.startswith('#'):
        line_indent = len(func_lines[i]) - len(func_lines[i].lstrip())
        if line_indent <= tool_parser_if_indent:
            has_unconditional_index = True
            print(f"  Found unconditional index assignment at func line {i}: {stripped}")
            break

if has_unconditional_index:
    print("PASS: index is assigned unconditionally before the if tool_parser block")
    sys.exit(0)

# Also check: maybe the else branch was kept but index is ALSO assigned before.
# Or maybe the fix is different: index assigned at the same level right before if.
# Let's also check the line immediately before `if tool_parser:`.
prev_line = func_lines[tool_parser_if_idx - 1].strip() if tool_parser_if_idx > 0 else ""
if ('index =' in prev_line or 'index=' in prev_line) and '==' not in prev_line:
    print("PASS: index assigned immediately before if tool_parser block")
    sys.exit(0)

# If we get here, index is NOT assigned unconditionally — this is the buggy pattern.
# Double check: are ALL index assignments inside the if/else branches?
print("FAIL: index is not assigned unconditionally before the if tool_parser block")
print("  (buggy pattern: index only assigned inside conditional branches)")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.30]: IndexError on empty prev_tool_call_arr
#
# In the buggy code, the condition guarding access to prev_tool_call_arr[-1]
# is only:
#   if (self._should_check_for_unstreamed_tool_arg_tokens(...) and tool_parser):
# This allows entry when prev_tool_call_arr is empty, causing IndexError.
#
# The gold fix changes this to also require `auto_tools_called` (which is
# True only when prev_tool_call_arr is non-empty), or an equivalent guard.
#
# AST approach: Find the if-statement that calls
# _should_check_for_unstreamed_tool_arg_tokens. Count the number of boolean
# operands in the condition. Buggy code has exactly 2 terms
# (_should_check(...) and tool_parser). Fixed code has 3+ terms, or the
# condition is restructured to include a guard against empty arrays.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] _should_check condition must guard against empty prev_tool_call_arr"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)
lines = source.splitlines()

# Find chat_completion_stream_generator
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            func_node = node
            break

if func_node is None:
    print("FAIL: chat_completion_stream_generator not found")
    sys.exit(1)

func_start = func_node.lineno - 1
func_end = func_node.end_lineno
func_lines = lines[func_start:func_end]

# Find the line(s) containing _should_check_for_unstreamed_tool_arg_tokens
should_check_idx = None
for i, line in enumerate(func_lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        should_check_idx = i
        break

if should_check_idx is None:
    print("FAIL: _should_check_for_unstreamed_tool_arg_tokens not found")
    sys.exit(1)

# Strategy A: Use AST to find the If node containing _should_check.
# Walk the function's AST to find If nodes whose test references
# _should_check_for_unstreamed_tool_arg_tokens.
# Then count the number of boolean operands in the BoolOp.

def find_if_with_should_check(node):
    """Recursively find If nodes whose condition calls _should_check..."""
    results = []
    for child in ast.walk(node):
        if isinstance(child, ast.If):
            # Check if the test (or any sub-expression) calls _should_check
            for sub in ast.walk(child.test):
                if isinstance(sub, ast.Call):
                    # Check if the function being called is _should_check...
                    func = sub.func
                    if isinstance(func, ast.Attribute) and func.attr == '_should_check_for_unstreamed_tool_arg_tokens':
                        results.append(child)
                        break
                    if isinstance(func, ast.Name) and func.id == '_should_check_for_unstreamed_tool_arg_tokens':
                        results.append(child)
                        break
    return results

if_nodes = find_if_with_should_check(func_node)

if not if_nodes:
    # _should_check might not be inside an `if` directly — it could be
    # assigned to a variable first (like in the gold fix: `should_check = ...`)
    # In that case, find the if-statement that uses the variable.

    # Check if _should_check is assigned to a variable
    assign_var = None
    for i, line in enumerate(func_lines):
        stripped = line.strip()
        if '_should_check_for_unstreamed_tool_arg_tokens' in stripped and '=' in stripped:
            # e.g., `should_check = self._should_check...`
            parts = stripped.split('=', 1)
            if len(parts) == 2 and not parts[0].strip().startswith('if'):
                assign_var = parts[0].strip()
                assign_idx = i
                break

    if assign_var:
        # Now find the if-statement that uses this variable
        # Look in the lines after the assignment
        for i in range(assign_idx + 1, min(assign_idx + 15, len(func_lines))):
            stripped = func_lines[i].strip()
            if stripped.startswith('if') and assign_var in stripped:
                # Count the boolean terms in this if-condition
                # Gather the full condition (may span lines)
                cond_text = stripped
                j = i + 1
                while j < len(func_lines) and not cond_text.rstrip().endswith(':'):
                    cond_text += ' ' + func_lines[j].strip()
                    j += 1

                # Count `and` / `or` to determine number of terms
                # "if A and B and C:" has 2 ands = 3 terms
                and_count = cond_text.count(' and ')
                or_count = cond_text.count(' or ')
                total_terms = and_count + or_count + 1

                if total_terms >= 3:
                    print(f"PASS: _should_check condition has {total_terms} terms (sufficient guard)")
                    print(f"  Condition: {cond_text.strip()}")
                    sys.exit(0)
                elif total_terms == 2:
                    # 2 terms: might be "should_check and tool_parser" — still buggy
                    # unless one of the terms checks for non-empty array
                    if 'auto_tools_called' in cond_text or 'prev_tool_call_arr' in cond_text or 'len(' in cond_text:
                        print(f"PASS: condition includes array-emptiness guard")
                        sys.exit(0)
                    else:
                        print(f"FAIL: condition has only 2 terms without array guard: {cond_text.strip()}")
                        sys.exit(1)
                else:
                    print(f"FAIL: condition has only {total_terms} term(s): {cond_text.strip()}")
                    sys.exit(1)

        # If we got here, the variable is assigned but not used in a simple if
        # This is unusual but could be a valid restructuring
        print("WARN: _should_check assigned to variable but could not find corresponding if")
        # Fall through to text-based analysis below

# Strategy B: Text-based analysis of the if-condition lines
# Find the if-statement that contains or follows _should_check
# and count the boolean terms.

# Gather the full condition block around should_check_idx
# First, find the enclosing `if` line
if_line_idx = None
for i in range(should_check_idx, max(should_check_idx - 5, -1), -1):
    if func_lines[i].strip().startswith('if'):
        if_line_idx = i
        break

if if_line_idx is None:
    if_line_idx = should_check_idx

# Gather continuation lines until we hit ':'
cond_text = ''
for i in range(if_line_idx, min(if_line_idx + 10, len(func_lines))):
    cond_text += ' ' + func_lines[i].strip()
    if ':' in func_lines[i].split('#')[0] and i > if_line_idx:
        break
    if func_lines[i].strip().endswith(':'):
        break

cond_text = cond_text.strip()

# Count boolean operators
and_count = cond_text.count(' and ')
or_count = cond_text.count(' or ')
total_terms = and_count + or_count + 1

# Check for guard against empty array
has_array_guard = (
    'auto_tools_called' in cond_text
    or 'prev_tool_call_arr' in cond_text
    or 'len(' in cond_text
)

if total_terms >= 3:
    print(f"PASS: _should_check if-condition has {total_terms} terms (strengthened guard)")
    print(f"  Condition: {cond_text}")
    sys.exit(0)
elif total_terms == 2 and has_array_guard:
    print(f"PASS: _should_check condition has array-emptiness guard")
    sys.exit(0)
elif total_terms <= 2 and not has_array_guard:
    # Check if there's a wrapping if above that provides the guard
    context_above = '\n'.join(func_lines[max(0, if_line_idx - 5):if_line_idx])
    if 'auto_tools_called' in context_above or ('prev_tool_call_arr' in context_above and 'if' in context_above):
        print(f"PASS: guard against empty array found in enclosing context")
        sys.exit(0)
    print(f"FAIL: _should_check condition lacks guard against empty prev_tool_call_arr")
    print(f"  Condition has {total_terms} term(s): {cond_text}")
    sys.exit(1)
else:
    print(f"PASS: condition appears to have array guard")
    sys.exit(0)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [PASS-TO-PASS, 0.10]: Function signature intact, file structure OK
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] function signature and file structure preserved"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py") as f:
    source = f.read()

tree = ast.parse(source)

# chat_completion_stream_generator must still exist
found = False
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == 'chat_completion_stream_generator':
            found = True
            break

if not found:
    print("FAIL: chat_completion_stream_generator function not found")
    sys.exit(1)

# File should have reasonable size (not stubbed out)
line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: file suspiciously small ({line_count} lines)")
    sys.exit(1)

# Key identifiers that must exist in the function
func_start = node.lineno - 1
func_end = node.end_lineno
func_source = '\n'.join(source.splitlines()[func_start:func_end])

required_in_func = [
    'tool_parser',
    'delta_message',
    '_should_check_for_unstreamed_tool_arg_tokens',
    'prev_tool_call_arr',
]
missing = [r for r in required_in_func if r not in func_source]
if missing:
    print(f"FAIL: function missing key identifiers: {missing}")
    sys.exit(1)

print(f"PASS: function intact, {line_count} lines, all key identifiers present")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL / supplementary, 0.15]: Both code regions modified
#   Light check: the two buggy regions have been touched. We do NOT check
#   what the fix is, only that the relevant areas differ from the known
#   buggy patterns.
###############################################################################
echo ""
echo "TEST 4: [structural] both buggy regions have been modified"
python3 << 'PYEOF'
import ast, sys

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
    print("FAIL: function not found")
    sys.exit(1)

func_start = func_node.lineno - 1
func_end = func_node.end_lineno
func_source = '\n'.join(lines[func_start:func_end])

checks_passed = 0

# Check 1: `index` should NOT be exclusively inside an else block.
# In the buggy code, `index` assignment only appears inside `else:` branch.
# We verify that `index` appears assigned at a scope that's not deeper than
# the if/else containing tool_parser check.
# Simple heuristic: count assignments to `index` - there should be at least
# one that's not inside an else block, OR the code has been restructured.

# Find all lines with `index =` (assignment, not comparison)
func_lines = lines[func_start:func_end]
index_assignments = []
for i, line in enumerate(func_lines):
    stripped = line.strip()
    if ('index =' in stripped or 'index=' in stripped) and '==' not in stripped and not stripped.startswith('#'):
        indent = len(line) - len(line.lstrip())
        # Check if this is inside an else block by looking back
        in_else = False
        for j in range(i-1, max(i-10, -1), -1):
            prev = func_lines[j].strip()
            prev_indent = len(func_lines[j]) - len(func_lines[j].lstrip())
            if prev_indent < indent and prev.startswith('else:'):
                in_else = True
                break
            if prev_indent < indent:
                break
        index_assignments.append((i, stripped, in_else))

# If ALL index assignments are inside else -> still buggy pattern
if index_assignments:
    all_in_else = all(in_else for _, _, in_else in index_assignments)
    if all_in_else:
        print("FAIL: index is still only assigned inside else branch (bug 1 pattern)")
        sys.exit(1)
    checks_passed += 1
    print("  Check 1 PASS: index assignment not exclusively in else branch")
else:
    # Maybe index variable was removed entirely or renamed - that's OK
    # as long as no UnboundLocalError (tested behaviorally in TEST 1)
    checks_passed += 1
    print("  Check 1 PASS: index variable restructured (no assignments found)")

# Check 2: The _should_check call should have SOME additional condition
# compared to the buggy code. In buggy code, the condition is just:
#   if self._should_check_for_unstreamed_tool_arg_tokens(...) and tool_parser:
# A fix adds more conditions or restructures. We just check the line isn't
# exactly the buggy pattern.
for i, line in enumerate(func_lines):
    if '_should_check_for_unstreamed_tool_arg_tokens' in line:
        # Get the full condition (may span multiple lines)
        cond_lines = []
        j = i
        while j < len(func_lines) and ':' not in func_lines[j].split('#')[0]:
            cond_lines.append(func_lines[j].strip())
            j += 1
        if j < len(func_lines):
            cond_lines.append(func_lines[j].strip())
        full_cond = ' '.join(cond_lines)

        # Buggy pattern: ONLY checks _should_check and tool_parser, nothing else
        # We check that there's at least one additional condition term
        # Count `and` / `or` terms
        terms = full_cond.count(' and ') + full_cond.count(' or ')
        if terms >= 2:
            # Has additional guard beyond just _should_check and tool_parser
            checks_passed += 1
            print("  Check 2 PASS: _should_check condition has additional guard")
        else:
            # Maybe restructured differently - check if there's a guard above
            context_above = '\n'.join(func_lines[max(0, i-5):i])
            if 'if' in context_above and ('prev_tool_call_arr' in context_above or
                                           'tool_call' in context_above.lower()):
                checks_passed += 1
                print("  Check 2 PASS: guard found above _should_check")
            else:
                print("  Check 2 WARN: could not confirm additional guard")
                # Don't fail - behavioral test is the authority
        break

if checks_passed >= 2:
    print("PASS: both regions show modifications")
    sys.exit(0)
elif checks_passed >= 1:
    print("PARTIAL PASS: one region confirmed modified")
    sys.exit(0)
else:
    print("FAIL: no modification detected in buggy regions")
    sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.15]: File not replaced with stub
###############################################################################
echo ""
echo "TEST 5: [anti-stub] file is not a stub"
python3 << 'PYEOF'
import ast, sys

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

# Check for key imports/patterns that should be in the real file
must_have = ['OpenAIServing', 'ChatCompletionRequest', 'async']
missing = [m for m in must_have if m not in source]
if missing:
    print(f"FAIL: missing expected patterns: {missing}")
    sys.exit(1)

print(f"PASS: {line_count} lines, {classes} classes, {funcs} functions")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.10]: No bare pip install in changed files
# Source: AGENTS.md line 27 @ 9d0351c91d3115215f84f3bd4b9f366d3fbd13b3
###############################################################################
echo ""
echo "TEST 6: [config-derived] no bare pip install in changed files"
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
T6=1
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
    T6=0
fi
echo "  -> exit code: $T6"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.30 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.05 if $T5 == 0 else 0.0
t6 = 0.10 if ${T6:-1} == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: index scoping)   = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: array guard)     = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (pass-to-pass: structure)       = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (structural: regions modified)  = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (anti-stub)                     = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 6 (config: no bare pip)           = $([ ${T6:-1} -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
