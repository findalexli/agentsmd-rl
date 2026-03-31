#!/usr/bin/env bash
set -uo pipefail

# NOTE: Zig code requires the full bun build system (Zig compiler, JavaScriptCore,
# cmake, etc.) and cannot be compiled or executed in the test container.
# All checks are structural, with comments stripped to prevent gaming.

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

FILE="src/bun.js/bindings/JSGlobalObject.zig"

##############################################################################
# GATE: File exists and is non-empty
##############################################################################
# [pr_diff] (gate): JSGlobalObject.zig must exist
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Helper: Zig-aware function extraction with comment stripping
##############################################################################
cat > /tmp/zig_extract.py << 'PYEOF'
import sys
import re

def strip_comments(code):
    """Remove single-line // comments from Zig code."""
    lines = code.split('\n')
    result = []
    for line in lines:
        in_string = False
        i = 0
        clean = line
        while i < len(line) - 1:
            if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                in_string = not in_string
            elif not in_string and line[i:i+2] == '//':
                clean = line[:i]
                break
            i += 1
        result.append(clean)
    return '\n'.join(result)

def extract_function(code, fn_name, signature_pattern=None):
    """Extract a function body by name, using brace-counting for boundaries.
    Returns the comment-stripped function body, or None if not found."""
    code = strip_comments(code)
    lines = code.split('\n')

    fn_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if signature_pattern:
            if re.search(signature_pattern, stripped):
                fn_start = i
                break
        else:
            if re.match(rf'pub fn {re.escape(fn_name)}\b', stripped) or \
               re.match(rf'fn {re.escape(fn_name)}\b', stripped):
                fn_start = i
                break

    if fn_start == -1:
        return None

    depth = 0
    started = False
    for i in range(fn_start, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                if not started:
                    started = True
                depth += 1
            elif ch == '}':
                depth -= 1
                if started and depth == 0:
                    return '\n'.join(lines[fn_start:i+1])
    return None

if __name__ == '__main__':
    filepath = sys.argv[1]
    fn_name = sys.argv[2]
    sig_pattern = sys.argv[3] if len(sys.argv) > 3 else None

    with open(filepath) as f:
        code = f.read()

    body = extract_function(code, fn_name, sig_pattern)
    if body:
        print(body)
    else:
        print("FUNCTION_NOT_FOUND")
PYEOF

##############################################################################
# BEHAVIORAL: Buggy crash-causing patterns REMOVED (0.40)
# These verify that the specific patterns causing the crash are gone.
# The most robust checks — can only pass by modifying the buggy code.
# (Comment injection defeated by stripping comments before analysis.)
##############################################################################

# [pr_diff] (0.15): throw()/throwPretty() must NOT have bun.assert(instance != .zero)
# This assert is THE crash trigger on stack overflow — must be removed for any fix.
add_total 0.15
BUGGY_ASSERT=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import strip_comments

with open('$FILE') as f:
    code = f.read()

clean = strip_comments(code)

# The buggy pattern: bun.assert(instance != .zero) must be ABSENT
if 'bun.assert(instance != .zero)' in clean:
    print('BUGGY')
else:
    print('FIXED')
")
if [ "$BUGGY_ASSERT" = "FIXED" ]; then
    add_score 0.15
    echo "PASS [0.15]: crash-causing bun.assert(instance != .zero) removed"
else
    echo "FAIL [0.15]: bun.assert(instance != .zero) still present — will crash"
fi

# [pr_diff] (0.15): throwValue() must NOT unconditionally call vm().throwError()
# without any guard. The bug: vm().throwError() hits releaseAssertNoException
# when an exception is already pending (e.g., after stack overflow).
add_total 0.15
THROWVALUE_GUARD=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'throwValue', r'pub fn throwValue\(')
if not body:
    print('MISSING')
    sys.exit()

# Accept any guard: hasException, hasPendingException, conditional, orelse
has_vm_throw = 'vm().throwError(' in body or 'vm().throw(' in body

if not has_vm_throw:
    # Doesn't call vm().throwError at all — delegated or refactored, valid
    print('FIXED')
else:
    # Still calls vm().throwError — must have SOME conditional guard
    has_guard = ('hasException' in body or
                 'hasPendingException' in body or
                 'if (' in body or
                 'orelse' in body)
    print('FIXED' if has_guard else 'BUGGY')
")
if [ "$THROWVALUE_GUARD" = "FIXED" ]; then
    add_score 0.15
    echo "PASS [0.15]: throwValue() has guard before vm error throw"
elif [ "$THROWVALUE_GUARD" = "MISSING" ]; then
    echo "FAIL [0.15]: throwValue() function not found"
else
    echo "FAIL [0.15]: throwValue() unconditionally calls vm().throwError()"
fi

# [pr_diff] (0.10): throwError(anyerror) must NOT directly call vm().throwError()
# without routing through a guarded path (throwValue or inline guard).
add_total 0.10
THROWERROR_SAFE=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'throwError', r'pub fn throwError\(this.*err:\s*anyerror')
if not body:
    print('MISSING')
    sys.exit()

# Should delegate to throwValue or have its own exception guard
has_safe_delegate = ('throwValue' in body or
                     'hasException' in body or
                     'hasPendingException' in body)

if has_safe_delegate:
    print('FIXED')
else:
    # Check if it still directly calls vm().throwError without any guard
    has_direct_vm = '.vm()' in body and 'throwError' in body.split('.vm()')[1][:30] if '.vm()' in body else False
    print('BUGGY' if has_direct_vm else 'FIXED')
")
if [ "$THROWERROR_SAFE" = "FIXED" ]; then
    add_score 0.10
    echo "PASS [0.10]: throwError(anyerror) uses safe throw path"
elif [ "$THROWERROR_SAFE" = "MISSING" ]; then
    echo "FAIL [0.10]: throwError(anyerror) function not found"
else
    echo "FAIL [0.10]: throwError(anyerror) directly calls vm().throwError() unguarded"
fi

##############################################################################
# BEHAVIORAL: Fix patterns present — flexible pattern matching (0.30)
# Accept multiple valid implementations: == .zero, orelse, catch, etc.
##############################################################################

# [pr_diff] (0.15): throw() and throwPretty() handle .zero from createErrorInstance
# Accept: == .zero, != .zero (inverted), orelse, catch, or error.JSError return
add_total 0.15
THROW_ZERO_HANDLE=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

passed = 0
for fn_name, sig in [
    ('throw', r'pub fn throw\(this.*comptime fmt'),
    ('throwPretty', r'pub fn throwPretty\('),
]:
    body = extract_function(code, fn_name, sig)
    if not body:
        continue

    has_create = 'createErrorInstance' in body
    # Accept any pattern that handles the failure case
    has_zero_handling = (
        '.zero' in body or
        'orelse' in body or
        'catch' in body or
        'error.JSError' in body
    )
    if has_create and has_zero_handling:
        passed += 1
    elif not has_create:
        # Refactored away from createErrorInstance — accept if handles errors
        if 'error.JSError' in body or 'JSError' in body:
            passed += 1

if passed >= 2:
    print('PASS')
elif passed >= 1:
    print('PARTIAL')
else:
    print('FAIL')
")
if [ "$THROW_ZERO_HANDLE" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: throw()/throwPretty() handle createErrorInstance failure"
elif [ "$THROW_ZERO_HANDLE" = "PARTIAL" ]; then
    add_score 0.07
    echo "PARTIAL [0.07/0.15]: only one of throw()/throwPretty() handles .zero"
else
    echo "FAIL [0.15]: throw()/throwPretty() don't handle createErrorInstance failure"
fi

# [pr_diff] (0.10): throwTODO() handles .zero from createErrorInstance
add_total 0.10
THROWTODO_HANDLE=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'throwTODO', r'pub fn throwTODO\(')
if not body:
    print('FAIL')
    sys.exit()

has_create = 'createErrorInstance' in body
has_zero_handling = (
    '.zero' in body or
    'orelse' in body or
    'catch' in body or
    'error.JSError' in body
)
if has_create and has_zero_handling:
    print('PASS')
elif not has_create and ('error.JSError' in body or 'JSError' in body):
    print('PASS')
else:
    print('FAIL')
")
if [ "$THROWTODO_HANDLE" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: throwTODO() handles createErrorInstance failure"
else
    echo "FAIL [0.10]: throwTODO() doesn't handle createErrorInstance failure"
fi

# [pr_diff] (0.05): createRangeError() handles .zero from createErrorInstance
add_total 0.05
CREATERANGE_HANDLE=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'createRangeError', r'pub fn createRangeError\(')
if not body:
    print('FAIL')
    sys.exit()

has_create = 'createErrorInstance' in body
has_zero_handling = (
    '.zero' in body or
    'orelse' in body or
    'catch' in body
)
if has_create and has_zero_handling:
    print('PASS')
else:
    print('FAIL')
")
if [ "$CREATERANGE_HANDLE" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: createRangeError() handles createErrorInstance failure"
else
    echo "FAIL [0.05]: createRangeError() doesn't handle createErrorInstance failure"
fi

##############################################################################
# REGRESSION: Pass-to-pass — existing functions preserved (0.10)
##############################################################################

# [pr_diff] (0.05): throwTypeError still exists with non-trivial body
add_total 0.05
TYPEERROR_EXISTS=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'throwTypeError', r'pub fn throwTypeError\(')
if body and len([l for l in body.strip().split('\n') if l.strip()]) > 3:
    print('PASS')
else:
    print('FAIL')
")
if [ "$TYPEERROR_EXISTS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: throwTypeError() preserved"
else
    echo "FAIL [0.05]: throwTypeError() missing or stubbed"
fi

# [pr_diff] (0.05): throwDOMException still exists with non-trivial body
add_total 0.05
DOMEXC_EXISTS=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_function

with open('$FILE') as f:
    code = f.read()

body = extract_function(code, 'throwDOMException', r'pub fn throwDOMException\(')
if body and len([l for l in body.strip().split('\n') if l.strip()]) > 3:
    print('PASS')
else:
    print('FAIL')
")
if [ "$DOMEXC_EXISTS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: throwDOMException() preserved"
else
    echo "FAIL [0.05]: throwDOMException() missing or stubbed"
fi

##############################################################################
# CONFIG: Agent config rules (0.15)
# Comments stripped to prevent gaming via comment injection.
##############################################################################

# [agent_config] (0.05): No inline @import in function bodies — src/CLAUDE.md:11
add_total 0.05
INLINE_IMPORTS=$(python3 -c "
import re, sys
sys.path.insert(0, '/tmp')
from zig_extract import strip_comments

with open('$FILE') as f:
    code = f.read()

clean = strip_comments(code)

in_fn = False
depth = 0
bad = False
for line in clean.split('\n'):
    stripped = line.strip()
    if re.match(r'(pub )?fn ', stripped) and '{' in stripped:
        in_fn = True
        depth = stripped.count('{') - stripped.count('}')
        continue
    if in_fn:
        depth += stripped.count('{') - stripped.count('}')
        if '@import' in stripped:
            bad = True
            break
        if depth <= 0:
            in_fn = False
print('FAIL' if bad else 'PASS')
")
if [ "$INLINE_IMPORTS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: no inline @import in functions (src/CLAUDE.md:11)"
else
    echo "FAIL [0.05]: found inline @import inside function body"
fi

# [agent_config] (0.05): Uses bun.assert not std.debug.assert — src/CLAUDE.md:16
add_total 0.05
STD_ASSERT=$(python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import strip_comments

with open('$FILE') as f:
    code = f.read()

clean = strip_comments(code)
count = clean.count('std.debug.assert')
print(count)
")
if [ "$STD_ASSERT" = "0" ]; then
    add_score 0.05
    echo "PASS [0.05]: uses bun.assert, not std.debug.assert (src/CLAUDE.md:16)"
else
    echo "FAIL [0.05]: uses std.debug.assert ($STD_ASSERT occurrences)"
fi

# [agent_config] (0.05): No std.fs / std.posix / std.os usage — src/CLAUDE.md:16
add_total 0.05
STD_FS=$(python3 -c "
import re, sys
sys.path.insert(0, '/tmp')
from zig_extract import strip_comments

with open('$FILE') as f:
    code = f.read()

clean = strip_comments(code)
count = len(re.findall(r'std\.(fs|posix|os)\.', clean))
print(count)
")
if [ "$STD_FS" = "0" ]; then
    add_score 0.05
    echo "PASS [0.05]: no std.fs/posix/os usage (src/CLAUDE.md:16)"
else
    echo "FAIL [0.05]: uses std.fs/posix/os ($STD_FS occurrences)"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.05)
##############################################################################

# [pr_diff] (0.05): File must have substantial content (not gutted)
add_total 0.05
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 400 ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub ($LINE_COUNT lines)"
else
    echo "FAIL [0.05]: file suspiciously small ($LINE_COUNT lines)"
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
reward = $FINAL
behavioral = min(reward, 0.70)
remainder = max(reward - 0.70, 0.0)
regression = min(remainder, 0.10)
remainder2 = max(remainder - 0.10, 0.0)
config = min(remainder2, 0.15)
structural = max(remainder2 - config, 0.0)
data = {
    'reward': round(reward, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config + structural, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
