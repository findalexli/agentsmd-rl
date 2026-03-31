#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
TARGET="$REPO/src/fd.zig"
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
# GATE: fd.zig must still be parseable and contain key structures
# WHY structural: Zig source requires full Bun build toolchain (cmake, zig
# compiler, etc.) — cannot compile or run fd.zig functions in this env.
# =============================================================================

# [pr_diff] GATE: fd.zig structural integrity
if python3 -c "
import sys
content = open('$TARGET').read()
if 'pub const FD = packed struct' not in content:
    sys.exit(1)
if 'fn fromJSValidated' not in content:
    sys.exit(1)
opens = content.count('{')
closes = content.count('}')
if abs(opens - closes) > 5:
    sys.exit(1)
"; then
    echo "GATE PASS: fd.zig structural integrity OK"
else
    echo "GATE FAIL: fd.zig has structural problems"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# =============================================================================
# Helper: extract fromJSValidated function body, stripping comments
# =============================================================================
EXTRACT_FUNC='
import re, sys

content = open("'$TARGET'").read()

# Extract fromJSValidated body
match = re.search(
    r"fn fromJSValidated\b[^{]*\{(.*?)(?=\n    (?:pub )?fn |\n    \};|\Z)",
    content, re.DOTALL
)
if not match:
    print("EXTRACT_FAIL", file=sys.stderr)
    sys.exit(1)

raw_body = match.group(1)

# Strip single-line comments (// ...) to prevent comment injection gaming
code_lines = []
for line in raw_body.split("\n"):
    stripped = line.strip()
    if stripped.startswith("//"):
        continue
    # Remove trailing comments
    no_comment = re.sub(r"//.*$", "", line)
    code_lines.append(no_comment)

code_body = "\n".join(code_lines)
# Also provide raw body for structural checks that need full content
'

# =============================================================================
# FAIL-TO-PASS 1 (0.35): Range validation on float BEFORE @intFromFloat
# WHY structural: compiled Zig — cannot call without full Bun rebuild
# The bug: @intFromFloat(float) panics when float is outside i64 range.
# The fix: validate float range BEFORE converting to integer.
# Accepts ANY pre-conversion range check (>=, <=, <, >, comparisons in either
# direction, helper functions, std.math checks, hardcoded constants, etc.)
# =============================================================================

# [pr_diff] (0.35): Float range is validated before @intFromFloat conversion
PASS_PRECHECK=0
if python3 -c "
import re, sys
$EXTRACT_FUNC

# Find line indices of key operations in COMMENT-FREE code
lines = code_body.split('\n')
range_check_line = None
int_from_float_line = None

for i, line in enumerate(lines):
    s = line.strip()
    if not s:
        continue

    # Detect @intFromFloat
    if int_from_float_line is None and '@intFromFloat' in s:
        int_from_float_line = i

    # Detect a range/bounds check on the float variable
    # Accept many patterns:
    #   float < 0, float >= 0, float > max, float <= max
    #   0 > float, max < float (reversed comparisons)
    #   std.math.isFinite(float), std.math.isNan(float)
    #   float > @as(f64, ...), float > @floatFromInt(...)
    #   Comparisons against numeric literals >= 2^31-1
    if range_check_line is None:
        # Direct float comparisons (either direction)
        has_float_cmp = bool(re.search(r'float\s*[<>=!]+\s*', s) or
                            re.search(r'[<>=!]+\s*float', s))
        # std.math checks on float
        has_math_check = bool(re.search(r'std\.math\.\w+\(float\)', s) or
                             re.search(r'isFinite|isNan|isInf', s))
        # Must relate to bounds (not the existing @mod check)
        is_mod_check = '@mod' in s
        if (has_float_cmp or has_math_check) and not is_mod_check:
            range_check_line = i

if range_check_line is None or int_from_float_line is None:
    sys.exit(1)
if range_check_line >= int_from_float_line:
    sys.exit(1)
" 2>/dev/null; then
    PASS_PRECHECK=1
fi
add_result 0.35 "$PASS_PRECHECK" "Float range validated before @intFromFloat conversion"

# =============================================================================
# FAIL-TO-PASS 2 (0.30): Range check gates conversion with an error path
# The fix must not just CHECK the range — it must RETURN an error or throw
# when the float is out of range. Otherwise the panic still occurs.
# =============================================================================

# [pr_diff] (0.30): Out-of-range float triggers error return before @intFromFloat
PASS_ERROR_PATH=0
if python3 -c "
import re, sys
$EXTRACT_FUNC

lines = code_body.split('\n')

# Find @intFromFloat position
int_from_float_line = None
for i, line in enumerate(lines):
    if '@intFromFloat' in line:
        int_from_float_line = i
        break

if int_from_float_line is None:
    sys.exit(1)

# In lines BEFORE @intFromFloat, look for:
# 1. A float comparison (range check)
# 2. Followed by an error action (return, throwRangeError, throwError, etc.)
pre_section = '\n'.join(lines[:int_from_float_line])

# Must have a float comparison
has_float_cmp = bool(
    re.search(r'float\s*[<>=!]+', pre_section) or
    re.search(r'[<>=!]+\s*float', pre_section) or
    re.search(r'(?:isFinite|isNan|isInf).*float', pre_section) or
    re.search(r'float.*(?:isFinite|isNan|isInf)', pre_section)
)

# Must have an error/return path tied to the check
has_error_path = bool(
    re.search(r'throwRangeError|throwError|return\s+.*error|return\s+.*null|return\s+\.err', pre_section, re.IGNORECASE) or
    re.search(r'return\s+globalThis', pre_section)
)

if not (has_float_cmp and has_error_path):
    sys.exit(1)
" 2>/dev/null; then
    PASS_ERROR_PATH=1
fi
add_result 0.30 "$PASS_ERROR_PATH" "Out-of-range float triggers error return before conversion"

# =============================================================================
# PASS-TO-PASS: Existing functionality preserved
# =============================================================================

# [pr_diff] (0.10): Non-integer float detection (@mod check) still present
PASS_MOD=0
if python3 -c "
import sys
content = open('$TARGET').read()
if '@mod(float, 1)' in content or '@mod(float, 1.0)' in content:
    sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    PASS_MOD=1
fi
add_result 0.10 "$PASS_MOD" "Non-integer float check (@mod) is preserved"

# [pr_diff] (0.10): @intFromFloat conversion still used for valid floats
PASS_CONV=0
if python3 -c "
import sys
$EXTRACT_FUNC
if '@intFromFloat' in code_body:
    sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    PASS_CONV=1
fi
add_result 0.10 "$PASS_CONV" "@intFromFloat conversion still present in fromJSValidated"

# =============================================================================
# REGRESSION: Function not gutted (anti-stub)
# =============================================================================

# [pr_diff] (0.05): fromJSValidated is substantive, not a stub
PASS_NOTSTUB=0
if python3 -c "
import re, sys
$EXTRACT_FUNC
code_only = [l for l in code_body.split('\n') if l.strip()]
if len(code_only) < 8:
    sys.exit(1)
# Must still have core operations
if 'throwRangeError' not in code_body:
    sys.exit(1)
if '@intCast' not in code_body:
    sys.exit(1)
if '@intFromFloat' not in code_body:
    sys.exit(1)
" 2>/dev/null; then
    PASS_NOTSTUB=1
fi
add_result 0.05 "$PASS_NOTSTUB" "fromJSValidated function body is not gutted"

# =============================================================================
# CONFIG-DERIVED: Agent config rules
# =============================================================================

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:11
PASS_NOINLINE=0
if python3 -c "
import re, sys
$EXTRACT_FUNC
if '@import(' in code_body:
    sys.exit(1)
" 2>/dev/null; then
    PASS_NOINLINE=1
fi
add_result 0.05 "$PASS_NOINLINE" "No inline @import inside fromJSValidated"

# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16
# std.math is exempted (numeric constants), but std.fs/std.posix/std.os are forbidden
PASS_BUNAPI=0
if python3 -c "
import re, sys
$EXTRACT_FUNC
for forbidden in ['std.fs.', 'std.posix.', 'std.os.']:
    if forbidden in code_body:
        sys.exit(1)
" 2>/dev/null; then
    PASS_BUNAPI=1
fi
add_result 0.05 "$PASS_BUNAPI" "No forbidden std.* API usage in fromJSValidated"

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
printf "$DETAILS"
echo ""
echo "Total: $SCORE / $TOTAL"

# Normalize to 1.0
if python3 -c "import sys; sys.exit(0 if float('$TOTAL') > 0 else 1)"; then
    FINAL=$(python3 -c "print(round(float('$SCORE') / float('$TOTAL'), 4))")
else
    FINAL="0.0"
fi

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt

# Compute category breakdowns
BEHAVIORAL=$(python3 -c "
s = 0.0
s += $PASS_PRECHECK * 0.35
s += $PASS_ERROR_PATH * 0.30
print(round(s, 4))
")

REGRESSION=$(python3 -c "
s = 0.0
s += $PASS_MOD * 0.10
s += $PASS_CONV * 0.10
s += $PASS_NOTSTUB * 0.05
print(round(s, 4))
")

CONFIG=$(python3 -c "
s = 0.0
s += $PASS_NOINLINE * 0.05
s += $PASS_BUNAPI * 0.05
print(round(s, 4))
")

echo "{\"reward\": $FINAL, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

echo ""
echo "Reward: $FINAL"
echo "Breakdown: behavioral=$BEHAVIORAL, regression=$REGRESSION, config=$CONFIG"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
