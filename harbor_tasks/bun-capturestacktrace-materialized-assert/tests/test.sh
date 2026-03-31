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

CPP_FILE="src/bun.js/bindings/FormatStackTraceForJS.cpp"

##############################################################################
# GATE: Source file exists and is non-empty
##############################################################################
# [pr_diff] (gate): FormatStackTraceForJS.cpp must exist
if [ ! -s "$CPP_FILE" ]; then
    echo "GATE FAILED: $CPP_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# HELPER: Extract function body with comments stripped
# WHY: C++ requires full Bun build toolchain (Zig, CMake, WebKit/JSC) and
# cannot be compiled or called in the test container.  All checks must be
# structural, but we strip comments to prevent trivial gaming.
##############################################################################

FUNC_BODY_STRIPPED=$(python3 << 'PYEOF'
import re, sys

text = open("src/bun.js/bindings/FormatStackTraceForJS.cpp").read()

# Extract errorConstructorFuncCaptureStackTrace body
m = re.search(
    r'errorConstructorFuncCaptureStackTrace\b(.*?)(?=\nJSC_DEFINE_HOST_FUNCTION|\Z)',
    text, re.DOTALL
)
if not m:
    print("__FUNC_NOT_FOUND__")
    sys.exit(0)

body = m.group(1)

# Strip C++ single-line comments
body = re.sub(r'//[^\n]*', '', body)
# Strip C++ block comments
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)
# Collapse runs of whitespace but keep newlines for line counting
print(body)
PYEOF
)

if [ "$FUNC_BODY_STRIPPED" = "__FUNC_NOT_FOUND__" ]; then
    echo "GATE FAILED: errorConstructorFuncCaptureStackTrace not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# FAIL-TO-PASS: Core bug checks (0.60 total)
# These verify the buggy pattern is ABSENT and a correct branching fix exists.
# WHY structural: C++ — cannot compile or execute.
##############################################################################

# [pr_diff] (0.25): BUGGY PATTERN MUST BE ABSENT — the old code has
# if (!hasMaterializedErrorInfo()) materializeErrorInfoIfNeeded(); then
# unconditionally calls setStackFrames(). A correct fix must branch on
# hasMaterializedErrorInfo with TWO DISTINCT PATHS (if/else), where
# setStackFrames is only in the non-materialized path.
add_total 0.25
BUGGY_ABSENT=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

# The buggy pattern: hasMaterializedErrorInfo used ONLY as a negated guard
# (if (!has...)) followed by unconditional setStackFrames. A correct fix
# uses hasMaterializedErrorInfo as a BRANCHING condition (if/else) where
# the two paths handle things differently.

# Check 1: must have hasMaterializedErrorInfo in an if-condition
has_if = re.search(r'\bif\s*\(.*hasMaterializedErrorInfo\s*\(', body)
if not has_if:
    print('FAIL'); sys.exit(0)

# Check 2: must have an else clause after the hasMaterializedErrorInfo if-block.
# The old code has no else — it just guards materializeErrorInfoIfNeeded then
# falls through to unconditional setStackFrames.
# Look for } else { or } else if after the hasMaterializedErrorInfo check.
after_if = body[has_if.start():]
has_else = bool(re.search(r'\}\s*else\s*\{', after_if))

if not has_else:
    # No else branch — still the buggy single-path pattern
    print('FAIL'); sys.exit(0)

# Check 3: if setStackFrames exists, it must NOT appear before the else
# (i.e., not in the materialized-path block)
set_sf = list(re.finditer(r'\bsetStackFrames\s*\(', after_if))
if set_sf:
    else_pos = re.search(r'\}\s*else\s*\{', after_if).start()
    any_before_else = any(m.start() < else_pos for m in set_sf)
    if any_before_else:
        # setStackFrames in the materialized path — still buggy
        print('FAIL')
    else:
        print('PASS')
else:
    # No setStackFrames at all — agent handles both paths with direct writes.
    # Acceptable alternative.
    print('PASS')
")
if [ "$BUGGY_ABSENT" = "PASS" ]; then
    add_score 0.25
    echo "PASS [0.25]: buggy unconditional-setStackFrames pattern is absent"
else
    echo "FAIL [0.25]: buggy unconditional-setStackFrames pattern still present"
fi

# [pr_diff] (0.20): hasMaterializedErrorInfo must be used as a BRANCHING
# condition with two distinct code paths (if + else). The old buggy code
# only uses it as a negated guard — if (!has...) materialize(); — with no
# else clause and unconditional setStackFrames after. A correct fix must
# have both branches.
add_total 0.20
IF_BRANCH=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

# Must use hasMaterializedErrorInfo in an if-condition
has_if = re.search(r'\bif\s*\(.*hasMaterializedErrorInfo\s*\(\s*\)', body)
if not has_if:
    print('FAIL'); sys.exit(0)

# Must have an else clause — two distinct paths, not just a guard
after_if = body[has_if.start():]
has_else = bool(re.search(r'\}\s*else\s*[\{]', after_if))
if has_else:
    print('PASS')
else:
    print('FAIL')
")
if [ "$IF_BRANCH" = "PASS" ]; then
    add_score 0.20
    echo "PASS [0.20]: hasMaterializedErrorInfo used as if-condition"
else
    echo "FAIL [0.20]: hasMaterializedErrorInfo not used as branching condition"
fi

# [pr_diff] (0.15): Materialized path must set .stack eagerly (not via lazy
# accessor). Any correct fix must write the stack value directly on the
# materialized branch — using putDirect, defineOwnProperty, putDirectWithout-
# Transition, or similar direct-write JSC API.  The key requirement is that
# it does NOT call setStackFrames on this path.
add_total 0.15
MATERIALIZED_PATH=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

# Find the if-branch on hasMaterializedErrorInfo
m = re.search(r'\bif\s*\(.*hasMaterializedErrorInfo\s*\(\s*\)', body)
if not m:
    print('FAIL'); sys.exit(0)

# Extract the code from the if-condition onwards
after_if = body[m.start():]

# Check for any direct-property-write API (accept multiple valid alternatives)
# putDirect, putDirectWithoutTransition, defineOwnProperty all work
has_direct_write = bool(re.search(
    r'\b(putDirect|putDirectWithoutTransition|defineOwnProperty)\s*\(',
    after_if
))

# Also need some form of stack computation (computeErrorInfo variants,
# or manual string building, or stackString — any approach that eagerly
# produces the stack value)
has_computation = bool(re.search(
    r'\b(computeErrorInfo|stackString|formatStackTrace|toWTFString|toString)\s*\(',
    after_if
))

if has_direct_write and has_computation:
    print('PASS')
elif has_direct_write:
    # Has direct write but computation might use a different API — partial credit
    print('PASS')
else:
    print('FAIL')
")
if [ "$MATERIALIZED_PATH" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: materialized path sets .stack eagerly via direct write"
else
    echo "FAIL [0.15]: materialized path missing direct property write"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15)
##############################################################################

# [pr_diff] (0.05): Non-materialized path still uses putDirectCustomAccessor
# to install a lazy getter. This preserves the lazy evaluation behavior for
# the common case where .stack hasn't been read yet.
add_total 0.05
LAZY_ACCESSOR=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

has_accessor = bool(re.search(r'\bputDirectCustomAccessor\s*\(', body))
if has_accessor:
    print('PASS')
else:
    print('FAIL')
")
if [ "$LAZY_ACCESSOR" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: non-materialized path preserves lazy custom accessor"
else
    echo "FAIL [0.05]: missing putDirectCustomAccessor for non-materialized path"
fi

# [pr_diff] (0.05): Function signature preserved — errorConstructorFuncCaptureStackTrace
# still exists with JSC_DEFINE_HOST_FUNCTION wrapper
add_total 0.05
if grep -q 'JSC_DEFINE_HOST_FUNCTION.*errorConstructorFuncCaptureStackTrace' "$CPP_FILE"; then
    add_score 0.05
    echo "PASS [0.05]: errorConstructorFuncCaptureStackTrace function preserved"
else
    echo "FAIL [0.05]: errorConstructorFuncCaptureStackTrace function missing"
fi

# [pr_diff] (0.05): The non-materialized path must still delete the existing
# .stack property before installing the custom accessor (DeletePropertySlot).
add_total 0.05
DELETE_PROP=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

has_delete = bool(re.search(r'\bdeleteProperty\s*\(', body))
if has_delete:
    print('PASS')
else:
    print('FAIL')
")
if [ "$DELETE_PROP" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: deleteProperty preserved for non-materialized path"
else
    echo "FAIL [0.05]: missing deleteProperty in non-materialized path"
fi

##############################################################################
# ANTI-STUB: Structural depth checks (0.10)
# WHY structural: C++ — cannot compile or execute.
##############################################################################

# [pr_diff] (0.05): Function must have substantial implementation — at least
# 35 non-blank, non-comment lines
add_total 0.05
FUNC_SIZE=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

lines = [l for l in body.strip().split('\n') if l.strip()]
if len(lines) >= 35:
    print('PASS')
else:
    print('FAIL')
")
if [ "$FUNC_SIZE" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: function has substantial implementation (anti-stub)"
else
    echo "FAIL [0.05]: function too small (possible stub)"
fi

# [pr_diff] (0.05): Must contain multiple distinct JSC API calls — not just
# keyword-stuffed. At least 4 different JSC APIs used in actual code.
add_total 0.05
API_DIVERSITY=$(python3 -c "
import re, sys

body = '''$FUNC_BODY_STRIPPED'''
if '__FUNC_NOT_FOUND__' in body:
    print('FAIL'); sys.exit(0)

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

apis = set()
api_patterns = [
    r'\bjsDynamicCast\s*<',
    r'\bRETURN_IF_EXCEPTION\s*\(',
    r'\bputDirect(CustomAccessor|WithoutTransition)?\s*\(',
    r'\bdeleteProperty\s*\(',
    r'\bsetStackFrames\s*\(',
    r'\bhasMaterializedErrorInfo\s*\(',
    r'\bmaterializeErrorInfoIfNeeded\s*\(',
    r'\bcomputeErrorInfo(ToJSValue)?\s*\(',
    r'\bgetFramesForCaller\s*\(',
    r'\bDeletePropertyModeScope\b',
]
for pat in api_patterns:
    if re.search(pat, body):
        apis.add(pat)

if len(apis) >= 4:
    print('PASS')
else:
    print('FAIL')
")
if [ "$API_DIVERSITY" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: sufficient JSC API diversity (anti-stub)"
else
    echo "FAIL [0.05]: insufficient JSC API diversity (possible stub)"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:4
# Bun C++ uses 4-space indentation. Check no tabs in the function body.
add_total 0.05
STYLE_CHECK=$(python3 -c "
import re
text = open('$CPP_FILE').read()
m = re.search(r'errorConstructorFuncCaptureStackTrace\b(.*?)(?=\nJSC_DEFINE_HOST_FUNCTION|\Z)', text, re.DOTALL)
if not m:
    print('FAIL')
else:
    body = m.group(1)
    if '\t' in body:
        print('FAIL')
    else:
        print('PASS')
")
if [ "$STYLE_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: code style consistent (no tabs in function body)"
else
    echo "FAIL [0.05]: code style violation (tabs found in function body)"
fi

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:4
# Must have RETURN_IF_EXCEPTION for proper exception safety in JSC code.
add_total 0.05
EXCEPTION_SAFETY=$(python3 -c "
import re

body = '''$FUNC_BODY_STRIPPED'''

body = re.sub(r'//[^\n]*', '', body)
body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)

has_exception_check = bool(re.search(r'\bRETURN_IF_EXCEPTION\s*\(', body))
if has_exception_check:
    print('PASS')
else:
    print('FAIL')
")
if [ "$EXCEPTION_SAFETY" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: proper exception handling with RETURN_IF_EXCEPTION"
else
    echo "FAIL [0.05]: missing RETURN_IF_EXCEPTION exception handling"
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
score = round($SCORE, 4)
# Behavioral: fail-to-pass checks (0.60 max)
behav = min(score, 0.60)
# Regression: pass-to-pass (0.15 max)
regr = min(max(score - 0.60, 0.0), 0.15)
# Structural/anti-stub (0.10 max)
struct_score = min(max(score - 0.75, 0.0), 0.10)
# Config-derived (0.10 max)
conf = min(max(score - 0.85, 0.0), 0.10)
data = {
    'reward': score,
    'behavioral': round(behav, 4),
    'regression': round(regr, 4),
    'config': round(conf, 4),
    'style_rubric': 0.0
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
