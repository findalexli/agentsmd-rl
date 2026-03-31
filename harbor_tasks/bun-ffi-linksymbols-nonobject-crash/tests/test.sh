#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
TARGET="$REPO/src/bun.js/api/ffi.zig"
SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" desc="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $desc\n"
    fi
}

# =============================================================================
# GATE: ffi.zig must still be structurally valid
# WHY structural: Zig requires full Bun build toolchain to compile
# =============================================================================

# [pr_diff] GATE: ffi.zig structural integrity
if python3 -c "
import sys
content = open('$TARGET').read()
opens = content.count('{')
closes = content.count('}')
if abs(opens - closes) > 5:
    sys.exit(1)
for name in ['pub const FFI = struct', 'fn generateSymbols(', 'fn generateSymbolForFunction(']:
    if name not in content:
        sys.exit(1)
"; then
    echo "GATE PASS: ffi.zig structural integrity OK"
else
    echo "GATE FAIL: ffi.zig has structural problems"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# =============================================================================
# Helper: extract Zig function body, strip comments
# =============================================================================
cat > /tmp/zig_extract.py << 'PYEOF'
import re, sys

def strip_zig_comments(code):
    """Remove // line comments from Zig source."""
    return re.sub(r'//[^\n]*', '', code)

def extract_fn_body(content, fn_name):
    """Extract function body by brace-matching, returns comment-stripped body."""
    # Find function start
    pattern = rf'fn {re.escape(fn_name)}\s*\('
    match = re.search(pattern, content)
    if not match:
        return None
    # Find opening brace
    pos = content.index('{', match.end())
    depth = 1
    start = pos + 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    body = content[start:i-1]
    return strip_zig_comments(body)

if __name__ == '__main__':
    content = open(sys.argv[1]).read()
    fn_name = sys.argv[2]
    body = extract_fn_body(content, fn_name)
    if body is None:
        sys.exit(1)
    print(body)
PYEOF

# =============================================================================
# FAIL-TO-PASS 1 (0.35): generateSymbols validates that property values are objects
# WHY structural: compiled Zig — cannot call without full Bun rebuild
# The bug: only isEmptyOrUndefinedOrNull() was checked, so primitives passed
# through to generateSymbolForFunction which asserts isObject(), causing panic.
# The fix must add validation that rejects non-object values BEFORE calling
# generateSymbolForFunction.
# =============================================================================

# [pr_diff] (0.35): generateSymbols rejects non-object property values before calling generateSymbolForFunction
PASS_F2P1=0
if python3 -c "
import re, sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_fn_body

content = open('$TARGET').read()
body = extract_fn_body(content, 'generateSymbols')
if body is None:
    sys.exit(1)

# The fix must add validation between the existing isEmptyOrUndefinedOrNull check
# and the call to generateSymbolForFunction. We check that:
# 1. There is SOME new validation beyond just isEmptyOrUndefinedOrNull
# 2. That validation relates to type/object checking
# 3. It appears in the code flow BEFORE generateSymbolForFunction is called

# Split body at generateSymbolForFunction call to get the validation section
parts = body.split('generateSymbolForFunction')
if len(parts) < 2:
    sys.exit(1)
before_call = parts[0]

# The original code only has isEmptyOrUndefinedOrNull. The fix must add
# something more. Accept any of these validation approaches:
validation_patterns = [
    r'isObject\s*\(',           # direct isObject check
    r'getObject\s*\(',          # getObject with null check
    r'jsType\s*\(',             # type tag check
    r'isNull\s*\(\s*\)',        # explicit null+type check combo
    r'@typeInfo',               # comptime type check
    r'isEmptyOrUndefinedOrNull.*(?:isObject|getObject|jsType)',  # extended existing check
    r'(?:isObject|getObject|jsType).*isEmptyOrUndefinedOrNull',  # reordered
]

found_validation = False
for pat in validation_patterns:
    if re.search(pat, before_call, re.DOTALL):
        found_validation = True
        break

# Also accept: the validation section has more conditional checks than the original
# (which only had isEmptyOrUndefinedOrNull). Count 'if' statements that involve
# type/object/value checking.
if not found_validation:
    # Accept any conditional that rejects values before generateSymbolForFunction
    # by checking if there's a new conditional with a return/continue/break/error
    # near the existing null check
    null_check_area = before_call[before_call.find('isEmptyOrUndefinedOrNull'):] if 'isEmptyOrUndefinedOrNull' in before_call else before_call
    # Look for additional branching after the null check that wasn't there before
    new_checks = re.findall(r'if\s*\([^)]*\)', null_check_area)
    if len(new_checks) >= 2:  # original has 1 (the null check), fix adds at least 1 more
        found_validation = True

if not found_validation:
    sys.exit(1)
" 2>/dev/null; then
    PASS_F2P1=1
fi
add_result 0.35 "$PASS_F2P1" "[pr_diff] generateSymbols rejects non-object property values"

# =============================================================================
# FAIL-TO-PASS 2 (0.20): Rejection produces a proper error, not a panic/skip
# =============================================================================

# [pr_diff] (0.20): Non-object rejection produces an error (not silent skip or panic)
PASS_F2P2=0
if python3 -c "
import re, sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_fn_body

content = open('$TARGET').read()
body = extract_fn_body(content, 'generateSymbols')
if body is None:
    sys.exit(1)

# The rejection path must produce an error. Accept any error mechanism:
error_patterns = [
    r'toTypeError',
    r'TypeError',
    r'toInvalidArguments',
    r'throwValue',
    r'createError',
    r'Expected an object',
    r'expected.*object',
    r'is not an object',
    r'must be an object',
]

# The error must appear in context with a type/object validation
# (not just the pre-existing null/undefined error)
# Strategy: look at the region around any new type-checking code
has_error_on_type_reject = False

# Find all blocks that could be the new validation
for error_pat in error_patterns:
    matches = list(re.finditer(error_pat, body, re.IGNORECASE))
    for m in matches:
        # Check if there's type-validation code within 500 chars of this error
        region_start = max(0, m.start() - 500)
        region_end = min(len(body), m.end() + 500)
        region = body[region_start:region_end]
        if any(re.search(vp, region) for vp in [r'isObject', r'getObject', r'jsType', r'@typeInfo']):
            has_error_on_type_reject = True
            break
    if has_error_on_type_reject:
        break

# Fallback: if the original isEmptyOrUndefinedOrNull block was extended
# (e.g., changed to `isEmptyOrUndefinedOrNull() or !isObject()`), the error
# is already in the existing block, so just check that the block was modified
if not has_error_on_type_reject:
    # Check if the null-check line was extended with additional conditions
    full_content = open('$TARGET').read()
    # Look for the combined condition pattern in the raw (with-comments) source
    if re.search(r'isEmptyOrUndefinedOrNull\(\).*(?:isObject|getObject|jsType)', full_content, re.DOTALL):
        # The existing error path now also covers non-objects
        has_error_on_type_reject = True
    if re.search(r'(?:isObject|getObject|jsType).*isEmptyOrUndefinedOrNull\(\)', full_content, re.DOTALL):
        has_error_on_type_reject = True

if not has_error_on_type_reject:
    sys.exit(1)
" 2>/dev/null; then
    PASS_F2P2=1
fi
add_result 0.20 "$PASS_F2P2" "[pr_diff] Non-object rejection produces proper error"

# =============================================================================
# FAIL-TO-PASS 3 (0.10): The validation change is in real code, not a no-op
# The actual Zig source must have the condition wired into control flow
# (i.e., the check leads to a return/continue/break/error, not dangling)
# =============================================================================

# [pr_diff] (0.10): New validation is wired into control flow (not dead code)
PASS_F2P3=0
if python3 -c "
import re, sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_fn_body

content = open('$TARGET').read()
body = extract_fn_body(content, 'generateSymbols')
if body is None:
    sys.exit(1)

# The validation must lead to a control flow change (return, continue, break, or error throw)
# Find type-check patterns and verify they're inside if-blocks with error/return paths
type_checks = [r'isObject', r'getObject', r'jsType', r'@typeInfo']
flow_keywords = ['return', 'continue', 'break', 'throwValue', 'toTypeError', 'toInvalidArguments']

found_wired = False
for tc in type_checks:
    for m in re.finditer(tc, body):
        # Look at the surrounding ~300 chars for control flow
        region = body[max(0, m.start()-100):min(len(body), m.end()+300)]
        for fk in flow_keywords:
            if fk in region:
                found_wired = True
                break
        if found_wired:
            break
    if found_wired:
        break

# Also accept: extended condition on the existing null-check line
# (the return/error is already there from the original code)
if not found_wired:
    # The original has: if (value.isEmptyOrUndefinedOrNull()) { ... return error ... }
    # If that condition was extended, the existing return handles it
    lines = body.split('\n')
    for line in lines:
        if 'isEmptyOrUndefinedOrNull' in line and any(tc_str in line for tc_str in ['isObject', 'getObject', 'jsType']):
            found_wired = True
            break

if not found_wired:
    sys.exit(1)
" 2>/dev/null; then
    PASS_F2P3=1
fi
add_result 0.10 "$PASS_F2P3" "[pr_diff] Validation wired into control flow (not dead code)"

# =============================================================================
# PASS-TO-PASS: Existing functionality preserved
# =============================================================================

# [repo_tests] (0.10): Core FFI functions and existing validation still intact
PASS_P2P=0
if python3 -c "
import sys
content = open('$TARGET').read()
required = [
    'pub const FFI = struct',
    'fn generateSymbols(',
    'fn generateSymbolForFunction(',
    'fn linkSymbols(',
    'fn print(',
    'fn open(',
    'isEmptyOrUndefinedOrNull()',  # existing check must not be removed
]
for r in required:
    if r not in content:
        print(f'MISSING: {r}')
        sys.exit(1)
" 2>/dev/null; then
    PASS_P2P=1
fi
add_result 0.10 "$PASS_P2P" "[repo_tests] Core FFI functions and existing null check still present"

# [repo_tests] (0.05): generateSymbolForFunction still has core processing logic
PASS_GEN=0
if python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_fn_body

content = open('$TARGET').read()
body = extract_fn_body(content, 'generateSymbolForFunction')
if body is None:
    sys.exit(1)
# Must still process args and returns
if 'args' not in body or 'returns' not in body:
    sys.exit(1)
# Must have more than trivial content
real_lines = [l for l in body.strip().split('\n') if l.strip()]
if len(real_lines) < 10:
    sys.exit(1)
" 2>/dev/null; then
    PASS_GEN=1
fi
add_result 0.05 "$PASS_GEN" "[repo_tests] generateSymbolForFunction still processes symbol descriptors"

# =============================================================================
# ANTI-STUB: generateSymbols is not hollowed out
# =============================================================================

# [pr_diff] (0.10): generateSymbols still iterates symbols and calls generateSymbolForFunction
PASS_STUB=0
if python3 -c "
import sys
sys.path.insert(0, '/tmp')
from zig_extract import extract_fn_body

content = open('$TARGET').read()
body = extract_fn_body(content, 'generateSymbols')
if body is None:
    sys.exit(1)
# Must still call generateSymbolForFunction
if 'generateSymbolForFunction' not in body:
    sys.exit(1)
# Must still have iteration logic (accept any iteration pattern)
has_iter = any(kw in body for kw in ['next()', 'while', 'for ', 'iterator', 'symbols_iter'])
if not has_iter:
    sys.exit(1)
# Must be substantial (not a trivial stub)
real_lines = [l for l in body.strip().split('\n') if l.strip()]
if len(real_lines) < 8:
    sys.exit(1)
" 2>/dev/null; then
    PASS_STUB=1
fi
add_result 0.10 "$PASS_STUB" "[pr_diff] generateSymbols contains iteration and function generation (anti-stub)"

# =============================================================================
# CONFIG-DERIVED: Rules from agent config files
# =============================================================================

# [agent_config] (0.10): No prohibited std.* APIs where bun.* exists — src/CLAUDE.md:16 @ 0de7a80
PASS_CONFIG=0
if python3 -c "
import subprocess, sys
# Try multiple diff strategies to find the agent's changes
for cmd in [['git', 'diff', 'HEAD'], ['git', 'diff', '--cached'], ['git', 'diff', 'HEAD~1']]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='$REPO')
    if result.stdout.strip():
        diff = result.stdout
        break
else:
    # No diff found — agent may not have committed. Check working tree against base.
    result = subprocess.run(['git', 'diff'], capture_output=True, text=True, cwd='$REPO')
    diff = result.stdout

added_lines = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
forbidden = ['std.fs', 'std.posix', 'std.os', 'std.process']
for line in added_lines:
    for f in forbidden:
        if f in line:
            sys.exit(1)
" 2>/dev/null; then
    PASS_CONFIG=1
fi
add_result 0.10 "$PASS_CONFIG" "[agent_config] No prohibited std.* APIs in new code — src/CLAUDE.md:16 @ 0de7a80"

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

# Normalize to 1.0
FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $SCORE)):.4f}')")

# Write results
mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
echo "$FINAL" > "$REPO/reward.txt"

BEH=$(python3 -c "print($PASS_F2P1 * 0.35 + $PASS_F2P2 * 0.20 + $PASS_F2P3 * 0.10)")
REG=$(python3 -c "print($PASS_P2P * 0.10 + $PASS_GEN * 0.05)")
STR=$(python3 -c "print($PASS_STUB * 0.10)")
CFG=$(python3 -c "print($PASS_CONFIG * 0.10)")
echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"structural\": $STR, \"config\": $CFG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"structural\": $STR, \"config\": $CFG, \"style_rubric\": 0.0}" > "$REPO/reward.json"

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
