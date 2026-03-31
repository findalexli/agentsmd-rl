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

##############################################################################
# Helper: strip Zig // line comments for gaming-resistant checks
# Writes comment-stripped code to stdout
##############################################################################
strip_zig_comments() {
    python3 -c "
import sys
with open(sys.argv[1]) as f:
    for line in f:
        idx = line.find('//')
        if idx >= 0:
            print(line[:idx])
        else:
            print(line, end='')
" "$1"
}

##############################################################################
# GATE: Zig source file exists and has balanced braces
##############################################################################
# [pr_diff] (gate): GlobWalker.zig must exist and have balanced braces
python3 -c "
import sys, os
target = 'src/glob/GlobWalker.zig'
if not os.path.exists(target):
    print('GATE FAILED: GlobWalker.zig does not exist')
    sys.exit(1)
code = open(target).read()
opens = code.count('{')
closes = code.count('}')
if abs(opens - closes) > 2:
    print(f'GATE FAILED: Severely unbalanced braces: {opens} open, {closes} close')
    sys.exit(1)
print('GATE PASS: Zig source file exists with balanced braces')
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: Zig source has structural errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# FAIL-TO-PASS (0.60 total)
# WHY structural: bun is a compiled Zig/C++ runtime; building requires the
# full Zig compiler + WebKit/JSC + CMake toolchain (multi-minute build).
# All checks operate on comment-stripped source to resist injection gaming.
##############################################################################

# [pr_diff] (0.20): The buggy computeNtFilter(component_idx) call is removed
# The base commit has this exact broken reference; any correct fix removes it.
# Check on comment-stripped code so a comment can't fool it.
STRIPPED=$(strip_zig_comments src/glob/GlobWalker.zig)
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
if 'computeNtFilter(component_idx)' in code:
    print('FAIL: Still references undeclared component_idx in code (not comments)')
    sys.exit(1)
print('PASS: Buggy component_idx reference removed from code')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.20
    echo "PASS [0.20]: Buggy computeNtFilter(component_idx) removed"
else
    add_total 0.20
    echo "FAIL [0.20]: Still references undeclared component_idx"
fi

# [pr_diff] (0.20): The fix derives a component index from the active BitSet
# Any correct fix must consult `active` (the BitSet that replaced component_idx)
# to get the index to pass to computeNtFilter. Check stripped code only.
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
lines = code.split('\n')

# Find setNameFilter call site and check that 'active' appears in actual code nearby
found = False
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'setNameFilter' in stripped and stripped and not stripped.startswith('//'):
        start = max(0, i - 15)
        end = min(len(lines), i + 5)
        context_lines = lines[start:end]
        # 'active' must appear in actual code lines (comments already stripped)
        for cl in context_lines:
            cl_stripped = cl.strip()
            if cl_stripped and 'active' in cl_stripped:
                found = True
                break
        break

if not found:
    print('FAIL: No reference to active BitSet in code near setNameFilter')
    sys.exit(1)
print('PASS: Fix references active BitSet near setNameFilter')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.20
    echo "PASS [0.20]: Fix uses active BitSet (verified in code, not comments)"
else
    add_total 0.20
    echo "FAIL [0.20]: Fix does not reference active BitSet in code"
fi

# [pr_diff] (0.20): Multi-active case handled — when multiple pattern components are
# active, applying a single-component NT filter would hide entries needed by other
# components. The fix must have conditional logic (if/else, switch, or ternary) that
# distinguishes single vs multiple active components.
# Accepts: count() == 1, count() != 1, count() > 1, popcount, or any comparison on active set size.
echo "$STRIPPED" | python3 -c "
import sys
import re
code = sys.stdin.read()
lines = code.split('\n')

found_conditional = False
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'setNameFilter' in stripped:
        start = max(0, i - 20)
        end = min(len(lines), i + 5)
        context = '\n'.join(lines[start:end])
        # Look for conditional logic on active set size in actual code
        # Accept: count() == 1, count() != 1, count() > 1, popcount, etc.
        if re.search(r'(count\(\)\s*[=!><]+\s*\d|popcount|\.len\s*[=!><])', context):
            found_conditional = True
        # Also accept: if (active.findFirstSet()) patterns with null checks
        if 'findFirstSet' in context and ('if' in context or 'else' in context):
            found_conditional = True
        break

if not found_conditional:
    print('FAIL: No conditional logic for single vs multi-active components')
    sys.exit(1)
print('PASS: Multi-active case has conditional logic')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.20
    echo "PASS [0.20]: Multi-active conditional logic present"
else
    add_total 0.20
    echo "FAIL [0.20]: No multi-active conditional handling"
fi

##############################################################################
# PASS-TO-PASS / REGRESSION (0.20 total)
##############################################################################

# [pr_diff] (0.10): setNameFilter is still called in the Windows block
# The fix must update the call, not delete the optimization entirely.
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
lines = code.split('\n')

# setNameFilter must exist in code (not just comments)
has_call = False
for line in lines:
    s = line.strip()
    if 'setNameFilter' in s and s:
        has_call = True
        break
if not has_call:
    print('FAIL: setNameFilter call removed entirely')
    sys.exit(1)
print('PASS: setNameFilter call preserved')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: setNameFilter call preserved"
else
    add_total 0.10
    echo "FAIL [0.10]: setNameFilter call removed"
fi

# [pr_diff] (0.10): computeNtFilter function still exists with u32 parameter
python3 -c "
import sys
code = open('src/glob/GlobWalker.zig').read()
if 'fn computeNtFilter' not in code:
    print('FAIL: computeNtFilter function was removed')
    sys.exit(1)
idx = code.index('fn computeNtFilter')
sig = code[idx:idx+200]
if 'u32' not in sig:
    print('FAIL: computeNtFilter signature changed — missing u32 param')
    sys.exit(1)
print('PASS: computeNtFilter function preserved')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: computeNtFilter function signature preserved"
else
    add_total 0.10
    echo "FAIL [0.10]: computeNtFilter function was modified or removed"
fi

##############################################################################
# ANTI-STUB (0.10)
##############################################################################

# [pr_diff] (0.10): computeNtFilter is still called (not just defined) near setNameFilter
# The fix should call computeNtFilter with the correct arg, not just pass null always.
# This also ensures the fix isn't a trivial deletion.
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
lines = code.split('\n')

set_filter_idx = None
compute_call_idx = None
for i, line in enumerate(lines):
    s = line.strip()
    if 'setNameFilter' in s:
        set_filter_idx = i
    # computeNtFilter call (not the function definition)
    if 'computeNtFilter' in s and 'fn computeNtFilter' not in s and 'fn ' not in s:
        compute_call_idx = i

if set_filter_idx is None:
    print('FAIL: setNameFilter not found in code')
    sys.exit(1)
if compute_call_idx is None:
    print('FAIL: computeNtFilter is never called (stub/deletion)')
    sys.exit(1)
if abs(set_filter_idx - compute_call_idx) > 20:
    print('FAIL: computeNtFilter call too far from setNameFilter (suspect relocation)')
    sys.exit(1)
print('PASS: computeNtFilter called near setNameFilter — non-trivial fix')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: Anti-stub — computeNtFilter still called near setNameFilter"
else
    add_total 0.10
    echo "FAIL [0.10]: Fix appears to be a stub or trivial deletion"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'setNameFilter' in line:
        start = max(0, i - 15)
        end = min(len(lines), i + 5)
        for j in range(start, end):
            s = lines[j].strip()
            if s and 'std.' in s and '@import' not in s:
                print(f'FAIL: std.* usage near fix (line ~{j})')
                sys.exit(1)
        break
print('PASS: No std.* usage near fix')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: [config] No std.* usage in fix — src/CLAUDE.md:16"
else
    add_total 0.05
    echo "FAIL [0.05]: [config] Fix uses std.* instead of bun.* APIs"
fi

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:10
echo "$STRIPPED" | python3 -c "
import sys
code = sys.stdin.read()
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'setNameFilter' in line:
        start = max(0, i - 15)
        end = min(len(lines), i + 5)
        for j in range(start, end):
            s = lines[j].strip()
            if s and '@import' in s:
                print(f'FAIL: Inline @import near fix (line ~{j})')
                sys.exit(1)
        break
print('PASS: No inline @import near fix')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: [config] No inline @import — src/CLAUDE.md:10"
else
    add_total 0.05
    echo "FAIL [0.05]: [config] Inline @import found near fix area"
fi

##############################################################################
# Final score
##############################################################################
FINAL=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "=== SCORE: $SCORE / $TOTAL = $FINAL ==="
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
s = $SCORE
t = $TOTAL
r = round(s/t, 4) if t > 0 else 0.0
# Breakdown by tier
behavioral = min(0.60, s)
regression = min(0.20, max(0, s - 0.60))
config = min(0.10, max(0, s - 0.80))
json.dump({'reward': r, 'behavioral': round(behavioral, 4), 'regression': round(regression, 4), 'config': round(config, 4), 'style_rubric': 0.0}, open('/logs/verifier/reward.json','w'))
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
