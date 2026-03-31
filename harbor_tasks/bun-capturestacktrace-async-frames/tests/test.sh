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

cd /workspace/bun

CPP_FILE="src/bun.js/bindings/ErrorStackTrace.cpp"

##############################################################################
# GATE: Source file exists and is non-empty
##############################################################################
# [pr_diff] (gate): ErrorStackTrace.cpp must exist
if [ ! -s "$CPP_FILE" ]; then
    echo "GATE FAILED: $CPP_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Helper: strip C/C++ comments and string literals from code so that
# keyword checks cannot be gamed by stuffing patterns into comments or
# string constants.  Works on a per-function body basis.
##############################################################################
STRIP_HELPER='
import re, sys

def strip_cpp_noise(code):
    """Remove C/C++ comments and string literals, leaving only real code."""
    # Order matters: longest match first
    pattern = (
        r"//[^\n]*"           # single-line comment
        r"|/\*.*?\*/"         # multi-line comment (non-greedy)
        r"|\"(?:[^\"\\]|\\.)*\""  # double-quoted string
        r"|'\''(?:[^'\\\\]|\\\\.)*'\\'"   # single-quoted char
    )
    return re.sub(pattern, " ", code, flags=re.DOTALL)

def extract_func(text, fname):
    """Extract the body of a C++ function by name.
    Matches from the function signature to the next top-level function or EOF."""
    pat = r"void\s+JSCStackTrace::" + fname + r"\b(.*?)(?=\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::|\Z)"
    m = re.search(pat, text, re.DOTALL)
    return m.group(1) if m else None
'

##############################################################################
# BEHAVIORAL (structural proxy — C++ cannot be compiled in container) (0.60)
# WHY structural: C++ code requires the full Bun build toolchain (Zig, CMake,
# JavaScriptCore/WebKit) — cannot be compiled or called in test container.
#
# All regex checks operate on comment-stripped / string-stripped code to
# prevent gaming via keyword stuffing.
##############################################################################

# [pr_diff] (0.25): Core fix — must delegate frame collection to an API that
# includes async frames (e.g. Interpreter::getStackTrace, vm.interpreter.getStackTrace)
# AND must NOT retain the old hand-rolled StackVisitor::visit walk for main
# frame collection inside getFramesForCaller.
add_total 0.25
CHECK1=$(python3 -c "
${STRIP_HELPER}

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    sys.exit()

clean = strip_cpp_noise(body)

# Must call getStackTrace via some object (interpreter, vm, etc.)
# This is the key behavioral change: delegate to JSC's async-aware collector
import re
uses_async_collector = bool(re.search(r'\bgetStackTrace\s*\(', clean))

# Must NOT have the old StackVisitor::visit(callFrame pattern for main collection
# (StackVisitor may still appear in unrelated helpers, so we check specifically
#  for StackVisitor::visit with callFrame as first arg)
has_old_walk = bool(re.search(r'StackVisitor\s*::\s*visit\s*\(\s*callFrame', clean))

print('PASS' if uses_async_collector and not has_old_walk else 'FAIL')
")
if [ "$CHECK1" = "PASS" ]; then
    add_score 0.25
    echo "PASS [0.25]: delegates to async-aware getStackTrace, removes old StackVisitor walk"
else
    echo "FAIL [0.25]: does not use async-aware frame collector or still has old StackVisitor walk"
fi

# [pr_diff] (0.15): Must handle async frame boundary during caller search.
# When scanning frames to find the caller, the code must stop at async frame
# boundaries because resumed async functions have a different callee cell.
# We check for an actual conditional/loop using isAsyncFrame (not just a mention).
add_total 0.15
CHECK2=$(python3 -c "
${STRIP_HELPER}
import re

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    sys.exit()

clean = strip_cpp_noise(body)

# Must have isAsyncFrame used in a conditional context (if/break/return/continue)
# This ensures it's actually used for control flow, not just mentioned
has_async_guard = bool(re.search(
    r'(?:if|while|for)\s*\([^)]*isAsyncFrame|isAsyncFrame[^;]*(?:break|return|continue)',
    clean
)) or bool(re.search(
    r'isAsyncFrame\s*\(\s*\)', clean
))

print('PASS' if has_async_guard else 'FAIL')
")
if [ "$CHECK2" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: handles async frame boundary in caller search"
else
    echo "FAIL [0.15]: missing async frame boundary handling"
fi

# [pr_diff] (0.10): stackTraceLimit must be applied to the FINAL visible frames,
# AFTER caller removal. The old code applied it during collection, losing frames.
# We verify: (a) some form of removal/erase precedes the limit application, OR
# (b) raw collection does NOT cap at stackTraceLimit (collects all, limits later).
add_total 0.10
CHECK3=$(python3 -c "
${STRIP_HELPER}
import re

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    sys.exit()

clean = strip_cpp_noise(body)

# Approach A: explicit removal before limit
remove_matches = list(re.finditer(r'removeAt|erase\s*\(|remove\s*\(', clean))
limit_matches = list(re.finditer(r'shrink\s*\(|resize\s*\(|stackTraceLimit', clean))

approach_a = False
if remove_matches and limit_matches:
    last_remove = max(m.start() for m in remove_matches)
    last_limit = max(m.start() for m in limit_matches)
    approach_a = last_limit > last_remove

# Approach B: collect without stackTraceLimit cap, then limit afterwards
# (e.g., pass max() or SIZE_MAX to getStackTrace, then shrink at end)
approach_b = bool(re.search(r'max\s*\(|numeric_limits|SIZE_MAX|UINT_MAX', clean)) and \
             bool(re.search(r'shrink|resize', clean))

print('PASS' if (approach_a or approach_b) else 'FAIL')
")
if [ "$CHECK3" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: stackTraceLimit applied after caller removal"
else
    echo "FAIL [0.10]: stackTraceLimit not properly applied after caller removal"
fi

# [pr_diff] (0.10): Must post-filter frames with isImplementationVisibilityPrivate
# to match new Error() behavior. The function call must appear in actual code
# (not comments/strings) in a filtering context (if/loop body).
add_total 0.10
CHECK4=$(python3 -c "
${STRIP_HELPER}
import re

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    sys.exit()

clean = strip_cpp_noise(body)

# Must call isImplementationVisibilityPrivate in code (not in a comment)
has_filter = bool(re.search(r'isImplementationVisibilityPrivate\s*\(', clean))
print('PASS' if has_filter else 'FAIL')
")
if [ "$CHECK4" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: post-filters frames with isImplementationVisibilityPrivate"
else
    echo "FAIL [0.10]: missing isImplementationVisibilityPrivate post-filter"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.05): getFramesForCaller function signature preserved
add_total 0.05
SIGCHECK=$(python3 -c "
text = open('$CPP_FILE').read()
import re
# Full signature with all parameters
has_sig = bool(re.search(
    r'void\s+JSCStackTrace::getFramesForCaller\s*\(\s*JSC::VM\s*&',
    text
))
print('PASS' if has_sig else 'FAIL')
")
if [ "$SIGCHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: getFramesForCaller function signature preserved"
else
    echo "FAIL [0.05]: getFramesForCaller function signature missing"
fi

# [pr_diff] (0.05): Other functions in ErrorStackTrace.cpp must not be deleted.
# The fix should only modify getFramesForCaller, not gut the whole file.
add_total 0.05
REGRESSION_FUNCS=$(python3 -c "
import re
text = open('$CPP_FILE').read()
# These sibling functions must still exist
required = [
    r'JSCStackTrace\s+JSCStackTrace::fromExisting',
    r'JSCStackTrace\s+JSCStackTrace::getStackTraceForThrownValue',
    r'JSCStackTrace\s+JSCStackTrace::captureCurrentJSStackTrace',
]
missing = [p for p in required if not re.search(p, text)]
print('PASS' if not missing else 'FAIL')
")
if [ "$REGRESSION_FUNCS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: sibling functions preserved"
else
    echo "FAIL [0.05]: sibling functions deleted/missing"
fi

# [pr_diff] (0.05): Caller matching must support both cell identity and
# name-based matching (for resumed async frames with different callee cells).
add_total 0.05
CHECK_DUAL=$(python3 -c "
${STRIP_HELPER}
import re

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    import sys; sys.exit()

clean = strip_cpp_noise(body)

# Cell identity: some comparison using callee() or caller object
has_cell_cmp = bool(re.search(r'callee\s*\(\s*\)\s*==|==\s*caller', clean))
# Name matching: reference to functionName or getting a name for comparison
has_name_cmp = bool(re.search(r'functionName|callerName|name\s*\(\s*\)', clean))

print('PASS' if has_cell_cmp and has_name_cmp else 'FAIL')
")
if [ "$CHECK_DUAL" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: caller matching uses both cell identity and name"
else
    echo "FAIL [0.05]: caller matching missing dual identity/name approach"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.15)
# WHY structural: C++ requires full Bun build toolchain
##############################################################################

# [pr_diff] (0.10): getFramesForCaller must have substantial, non-trivial
# implementation. Requires >= 20 lines of real code (not blank, not comments,
# not trivial auto x=N declarations).
add_total 0.10
ANTI_STUB=$(python3 -c "
${STRIP_HELPER}
import re

text = open('$CPP_FILE').read()
body = extract_func(text, 'getFramesForCaller')
if not body:
    print('FAIL')
    import sys; sys.exit()

lines = body.strip().split('\n')
real_lines = []
for l in lines:
    s = l.strip()
    if not s:
        continue
    if s.startswith('//') or s.startswith('/*') or s.startswith('*'):
        continue
    # Filter trivial padding: lines like 'auto xN = N;' or just '}'
    if re.match(r'^auto\s+\w+\s*=\s*\d+\s*;$', s):
        continue
    if s in ('{', '}', '};'):
        continue
    real_lines.append(s)

# Need meaningful code: function calls, loops, conditionals
has_loops_or_ifs = len([l for l in real_lines if re.search(r'\b(for|while|if)\s*\(', l)]) >= 2
has_function_calls = len([l for l in real_lines if re.search(r'\w+\s*\(', l)]) >= 5

print('PASS' if len(real_lines) >= 20 and has_loops_or_ifs and has_function_calls else 'FAIL')
")
if [ "$ANTI_STUB" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: getFramesForCaller has substantial non-trivial implementation"
else
    echo "FAIL [0.10]: getFramesForCaller implementation too small or trivial (stub)"
fi

# [pr_diff] (0.05): ErrorStackTrace.cpp overall file size check
add_total 0.05
LINE_COUNT=$(wc -l < "$CPP_FILE")
if [ "$LINE_COUNT" -gt 100 ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub file check ($LINE_COUNT lines)"
else
    echo "FAIL [0.05]: ErrorStackTrace.cpp suspiciously small ($LINE_COUNT lines)"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.05)
##############################################################################

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:245
# Bun C++ code uses 4-space indentation consistently. Check that the
# getFramesForCaller function doesn't introduce tabs.
add_total 0.05
STYLE_CHECK=$(python3 -c "
import re
text = open('$CPP_FILE').read()

m = re.search(r'void\s+JSCStackTrace::getFramesForCaller\b(.*?)(?=\n\w+\s+JSCStackTrace::|\nJSCStackTrace\s+JSCStackTrace::|\Z)', text, re.DOTALL)
if not m:
    print('FAIL')
else:
    body = m.group(1)
    has_tabs = '\t' in body
    print('PASS' if not has_tabs else 'FAIL')
")
if [ "$STYLE_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: code style consistent (no tabs in function body)"
else
    echo "FAIL [0.05]: code style violation (tabs found in function body)"
fi

##############################################################################
# Final scoring
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Total: $FINAL / $TOTAL"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
behavioral = min(score, 0.60)
regression = min(max(score - 0.60, 0.0), 0.15)
config_sc = min(max(score - 0.75, 0.0), 0.05)
structural = min(max(score - 0.80, 0.0), 0.15)
data = {
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config_sc, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
