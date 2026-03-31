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
# GATE: ffi.zig must still be structurally valid Zig
# WHY structural: Zig requires full Bun build toolchain to compile+run
# =============================================================================

# [pr_diff] GATE: ffi.zig parses as valid Zig (balanced braces, key structs present)
if python3 -c "
import sys
content = open('$TARGET').read()
opens = content.count('{')
closes = content.count('}')
if abs(opens - closes) > 5:
    sys.exit(1)
if 'pub const FFI = struct' not in content:
    sys.exit(1)
if 'generateSymbols' not in content:
    sys.exit(1)
"; then
    echo "GATE PASS: ffi.zig structural integrity OK"
else
    echo "GATE FAIL: ffi.zig has structural problems"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# =============================================================================
# Helper: strip Zig comments to prevent comment-injection gaming
# =============================================================================
python3 -c "
import re
content = open('$TARGET').read()
# Strip single-line Zig comments (// ...)
stripped = re.sub(r'//[^\n]*', '', content)
open('/tmp/ffi_stripped.zig', 'w').write(stripped)
"

# =============================================================================
# FAIL-TO-PASS 1 (0.30): The value guard in generateSymbols rejects non-object values
# WHY structural: Zig compiled code — cannot call without full Bun rebuild
# The bug: isEmptyOrUndefinedOrNull() alone lets numbers/strings/booleans through.
# The fix must add SOME additional type guard beyond just isEmptyOrUndefinedOrNull.
# We accept any approach: isObject(), type tag check, switch, etc.
# =============================================================================

# [pr_diff] (0.30): generateSymbols has additional type validation beyond isEmptyOrUndefinedOrNull
PASS_GUARD=0
if python3 -c "
import re, sys

stripped = open('/tmp/ffi_stripped.zig').read()
idx = stripped.find('generateSymbols')
if idx == -1:
    sys.exit(1)

region = stripped[idx:idx+5000]

# Find the while loop that iterates symbols
loop_idx = region.find('while')
if loop_idx == -1:
    sys.exit(1)
loop_region = region[loop_idx:loop_idx+1500]

# The buggy code only has isEmptyOrUndefinedOrNull. A correct fix adds
# an additional guard. We accept ANY of these patterns:
# - isObject() (gold patch approach)
# - type tag comparison (e.g., @intFromEnum, .tag)
# - isStruct, isCallable, or other type-checking method
# - switch on value type
# The key signal: the condition around isEmptyOrUndefinedOrNull must have
# been EXTENDED with additional logic (an 'or' clause, an 'and' clause,
# or a separate if block before generateSymbolForFunction)

has_isempty = 'isEmptyOrUndefinedOrNull' in loop_region

# Check for object/type validation beyond the original guard
type_checks = [
    'isObject',
    'isStruct',
    'isCallable',
    '@intFromEnum',
    '.tag',
    'isFunction',
    'typeof',
    'jsType',
]
has_type_check = any(tc in loop_region for tc in type_checks)

# Also accept: the isEmptyOrUndefinedOrNull line has been extended with 'or'
# to include additional logic on the same condition
lines_with_empty = [l for l in loop_region.split('\n') if 'isEmptyOrUndefinedOrNull' in l]
extended_condition = any(' or ' in l or ' and ' in l for l in lines_with_empty if 'isEmptyOrUndefinedOrNull' in l)

if not (has_type_check or extended_condition):
    sys.exit(1)
" 2>/dev/null; then
    PASS_GUARD=1
fi
add_result 0.30 "$PASS_GUARD" "[pr_diff] Symbol value guard extended beyond isEmptyOrUndefinedOrNull"

# =============================================================================
# FAIL-TO-PASS 2 (0.15): TypeError error path preserved for invalid descriptors
# WHY structural: Zig compiled code — cannot call without full Bun rebuild
# =============================================================================

# [pr_diff] (0.15): toTypeError call site still present in generateSymbols for bad values
PASS_ERROR=0
if python3 -c "
import sys

stripped = open('/tmp/ffi_stripped.zig').read()
idx = stripped.find('generateSymbols')
if idx == -1:
    sys.exit(1)
region = stripped[idx:idx+5000]

# The error path must produce a TypeError — accept various message wordings
# but require toTypeError is called in this function
if 'toTypeError' not in region:
    sys.exit(1)

# Must have some error message about the value being wrong type
# Accept: 'Expected an object', 'must be an object', 'invalid', 'not an object', etc.
error_indicators = ['Expected an object', 'must be an object', 'not an object',
                    'invalid', 'Invalid', 'object for key', 'descriptor']
if not any(ind in region for ind in error_indicators):
    sys.exit(1)
" 2>/dev/null; then
    PASS_ERROR=1
fi
add_result 0.15 "$PASS_ERROR" "[pr_diff] TypeError path for invalid symbol descriptors"

# =============================================================================
# FAIL-TO-PASS 3 (0.25): Memory leak fix — arg_types.deinit in error-return paths
# WHY structural: Zig compiled code — cannot call without full Bun rebuild
# The PR adds arg_types.deinit(allocator) in error cleanup for print, open,
# and linkSymbols. Without this, parsed arg_types arrays leak on error returns.
# =============================================================================

# [pr_diff] (0.25): arg_types cleanup added in error-return paths
PASS_MEMLEAK=0
if python3 -c "
import sys

stripped = open('/tmp/ffi_stripped.zig').read()

# The PR adds arg_types.deinit in 3 error-return paths (print, open, linkSymbols).
# Each of these functions has a cleanup block that frees symbol keys and then
# clears the symbols map. The fix adds arg_types.deinit between the key-free
# loop and clearAndFree.
#
# We check: in the vicinity of 'clearAndFree' calls (the cleanup pattern),
# there should be references to 'arg_types' cleanup (deinit or free).
# The buggy code does NOT have arg_types cleanup near clearAndFree.

# Find all clearAndFree sites (there are several in the file)
parts = stripped.split('clearAndFree')
if len(parts) < 3:
    # Need at least 3 clearAndFree calls (print, open, linkSymbols error paths)
    sys.exit(1)

# For each clearAndFree, look backward ~500 chars for arg_types cleanup
cleanup_count = 0
for i in range(1, len(parts)):
    preceding = parts[i-1][-500:]
    if 'arg_types' in preceding and ('deinit' in preceding or 'free' in preceding):
        cleanup_count += 1

# The PR fixes 3 error paths — require at least 2 to be lenient
if cleanup_count < 2:
    sys.exit(1)
" 2>/dev/null; then
    PASS_MEMLEAK=1
fi
add_result 0.25 "$PASS_MEMLEAK" "[pr_diff] arg_types memory cleanup in error-return paths"

# =============================================================================
# PASS-TO-PASS: Core FFI structure intact
# =============================================================================

# [repo_tests] (0.10): Core FFI struct and key methods still present (stripped source)
PASS_P2P=0
if python3 -c "
import sys
stripped = open('/tmp/ffi_stripped.zig').read()
required = [
    'pub const FFI = struct',
    'generateSymbols',
    'generateSymbolForFunction',
    'symbols_iter',
    'isEmptyOrUndefinedOrNull',
]
for r in required:
    if r not in stripped:
        print(f'MISSING: {r}')
        sys.exit(1)
" 2>/dev/null; then
    PASS_P2P=1
fi
add_result 0.10 "$PASS_P2P" "[repo_tests] Core FFI struct and symbol generation methods intact"

# =============================================================================
# ANTI-STUB: The fix is not a trivial stub
# =============================================================================

# [pr_diff] (0.05): generateSymbols still has substantive symbol parsing logic
PASS_STUB=0
if python3 -c "
import sys
stripped = open('/tmp/ffi_stripped.zig').read()
idx = stripped.find('generateSymbols')
if idx == -1:
    sys.exit(1)
region = stripped[idx:idx+5000]

# Must still have all core logic indicators (in comment-stripped source)
indicators = ['symbols_iter', 'generateSymbolForFunction', 'toTypeError',
              'isEmptyOrUndefinedOrNull', 'clearAndFree']
found = sum(1 for ind in indicators if ind in region)
if found < 4:
    sys.exit(1)
" 2>/dev/null; then
    PASS_STUB=1
fi
add_result 0.05 "$PASS_STUB" "[pr_diff] Symbol parsing logic still substantive (anti-stub)"

# =============================================================================
# CONFIG-DERIVED: Rules from agent config files
# =============================================================================

# [agent_config] (0.15): No use of std.* APIs where bun.* equivalents exist — src/CLAUDE.md:16 @ 0de7a80
PASS_CONFIG=0
if python3 -c "
import subprocess, sys

result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, cwd='$REPO')
diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, cwd='$REPO')
    diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', 'HEAD~1'], capture_output=True, text=True, cwd='$REPO')
    diff = result.stdout

# If there's no diff at all, agent hasn't made changes — fail this check
# (prevents gaming by doing nothing)
if not diff.strip():
    sys.exit(1)

# Check added lines for prohibited std.* usage
added_lines = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
forbidden = ['std.fs', 'std.posix', 'std.os', 'std.process']
for line in added_lines:
    for f in forbidden:
        if f in line:
            sys.exit(1)
" 2>/dev/null; then
    PASS_CONFIG=1
fi
add_result 0.15 "$PASS_CONFIG" "[agent_config] No prohibited std.* APIs in new code — src/CLAUDE.md:16 @ 0de7a80"

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

# Normalize to 1.0
FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $SCORE)):.4f}')")

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt

BEH=$(python3 -c "print($PASS_GUARD * 0.30 + $PASS_ERROR * 0.15 + $PASS_MEMLEAK * 0.25)")
REG=$(python3 -c "print($PASS_P2P * 0.10)")
STUB=$(python3 -c "print($PASS_STUB * 0.05)")
CFG=$(python3 -c "print($PASS_CONFIG * 0.15)")
echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"anti_stub\": $STUB, \"config\": $CFG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
