#!/usr/bin/env bash
set +e

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
# GATE: Zig syntax check — abort on failure
##############################################################################
# [pr_diff] (gate): Modified Zig files must have balanced braces
python3 -c "
import sys
for path in ['src/glob/GlobWalker.zig', 'src/collections/bit_set.zig']:
    try:
        code = open(path).read()
    except FileNotFoundError:
        print(f'GATE FAILED: {path} not found')
        sys.exit(1)
    opens = code.count('{')
    closes = code.count('}')
    if abs(opens - closes) > 2:
        print(f'GATE FAILED: {path} unbalanced: {opens} open, {closes} close')
        sys.exit(1)
print('GATE PASS: Zig source files have balanced braces')
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: Zig source has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# FAIL-TO-PASS STRUCTURAL (0.35 total)
# WHY structural: Zig requires full Zig compiler + WebKit/JSC + CMake
# toolchain (2.5+ min build). Cannot call code, so we verify the semantic
# change: double-push bug pattern removed, single-index WorkItem replaced.
##############################################################################

# [pr_diff] (0.20): Double-push bug pattern removed
# The ROOT CAUSE is `recursion_idx_bump == 2` which forks into two
# workbuf.append calls for the same directory. ANY correct fix removes this.
# Also checks that total workbuf.append count decreased (base has 6, fix ~3).
python3 -c "
import sys
code = open('src/glob/GlobWalker.zig').read()

if 'recursion_idx_bump == 2' in code:
    print('FAIL: Still has recursion_idx_bump == 2 (the double-push branch)')
    sys.exit(1)

if 'recursion_idx_bump' in code:
    print('FAIL: Still references recursion_idx_bump (old forking variable)')
    sys.exit(1)

# The base code has 6 workbuf.append calls (pairs in if/else blocks).
# A correct fix consolidates to one append per code path (~3).
append_count = code.count('workbuf.append')
if append_count >= 6:
    print(f'FAIL: Still has {append_count} workbuf.append calls (base has 6, fix should reduce)')
    sys.exit(1)

print(f'PASS: Double-push removed (workbuf.append count: {append_count})')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.20
    echo "PASS (0.20): Double-push bug pattern removed"
else
    add_total 0.20
    echo "FAIL (0.20): Double-push bug pattern removed"
fi

# [pr_diff] (0.15): WorkItem changed from single u32 index to collection type
# Base code has `idx: u32` in WorkItem. Fix must replace with ANY collection
# (bitset, hashmap, array, etc.) that can track multiple indices.
python3 -c "
import re, sys
code = open('src/glob/GlobWalker.zig').read()

# Find WorkItem struct and extract its body
wi_match = re.search(r'const WorkItem = struct\s*\{', code)
if not wi_match:
    print('FAIL: WorkItem struct not found')
    sys.exit(1)

start = wi_match.end()
depth = 1
pos = start
while pos < len(code) and depth > 0:
    if code[pos] == '{': depth += 1
    elif code[pos] == '}': depth -= 1
    pos += 1
struct_body = code[wi_match.start():pos]

# Old field must be gone
if re.search(r'\bidx\s*:\s*u32\b', struct_body):
    print('FAIL: WorkItem still has idx: u32 (single index)')
    sys.exit(1)

# WorkItem.new() second param must not be bare u32
new_fn = re.search(r'fn\s+new\s*\(([^)]+)\)', struct_body)
if new_fn:
    params = [p.strip() for p in new_fn.group(1).split(',')]
    if len(params) >= 2 and re.search(r':\s*u32\s*$', params[1]):
        print('FAIL: WorkItem.new() still takes u32 index parameter')
        sys.exit(1)

print('PASS: WorkItem uses collection type instead of single idx: u32')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.15
    echo "PASS (0.15): WorkItem uses collection instead of single idx"
else
    add_total 0.15
    echo "FAIL (0.15): WorkItem uses collection instead of single idx"
fi

##############################################################################
# CORE FIX VERIFICATION (0.25 total)
# These verify the semantic fix: directory/file evaluation now iterates
# over multiple active indices. Accepts ANY iteration mechanism.
##############################################################################

# [pr_diff] (0.15): matchPatternDir called inside iteration over active indices
# Accepts: .iterator(), for loop, while + findFirstSet, any iteration pattern.
python3 -c "
import re, sys
code = open('src/glob/GlobWalker.zig').read()

iteration_patterns = [
    r'\.iterator\s*\(',           # bitset/hashmap iterator
    r'while\s*\(.+\.next\(\)',    # while (it.next())
    r'for\s*\(.+\.items\)',       # for (array.items)
    r'while\s*\(.+findFirstSet',  # while (set.findFirstSet())
]

dir_calls = list(re.finditer(r'matchPatternDir\s*\(', code))
if not dir_calls:
    print('FAIL: matchPatternDir not called anywhere')
    sys.exit(1)

found = False
for call in dir_calls:
    region_start = max(0, call.start() - 1200)
    region = code[region_start:call.end() + 200]
    for pat in iteration_patterns:
        if re.search(pat, region):
            found = True
            break
    if found:
        break

if not found:
    print('FAIL: matchPatternDir not called inside any iteration over indices')
    sys.exit(1)

print('PASS: matchPatternDir called within multi-index iteration')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.15
    echo "PASS (0.15): Multi-index iteration for directory evaluation"
else
    add_total 0.15
    echo "FAIL (0.15): Multi-index iteration for directory evaluation"
fi

# [pr_diff] (0.10): matchPatternFile also called inside iteration
python3 -c "
import re, sys
code = open('src/glob/GlobWalker.zig').read()

iteration_patterns = [
    r'\.iterator\s*\(',
    r'while\s*\(.+\.next\(\)',
    r'for\s*\(.+\.items\)',
    r'while\s*\(.+findFirstSet',
]

file_calls = list(re.finditer(r'matchPatternFile\s*\(', code))
if not file_calls:
    print('FAIL: matchPatternFile not called anywhere')
    sys.exit(1)

found = False
for call in file_calls:
    region_start = max(0, call.start() - 1200)
    region = code[region_start:call.end() + 200]
    for pat in iteration_patterns:
        if re.search(pat, region):
            found = True
            break
    if found:
        break

if not found:
    print('FAIL: matchPatternFile not called inside any iteration over indices')
    sys.exit(1)

print('PASS: matchPatternFile called within multi-index iteration')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): File matching iterates active indices"
else
    add_total 0.10
    echo "FAIL (0.10): File matching iterates active indices"
fi

##############################################################################
# REGRESSION: Pass-to-pass (0.15 total)
##############################################################################

# [pr_diff] (0.10): Core matching functions still defined
python3 -c "
import sys
code = open('src/glob/GlobWalker.zig').read()
missing = []
for fn in ['matchPatternDir', 'matchPatternFile', 'matchPatternImpl']:
    if f'fn {fn}' not in code:
        missing.append(fn)
if missing:
    print(f'FAIL: Core matching functions removed: {missing}')
    sys.exit(1)
print('PASS: Core matching functions preserved')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): Core matching functions preserved"
else
    add_total 0.10
    echo "FAIL (0.10): Core matching functions preserved"
fi

# [pr_diff] (0.05): WorkItem still has path and kind fields
python3 -c "
import re, sys
code = open('src/glob/GlobWalker.zig').read()
wi_match = re.search(r'const WorkItem = struct\s*\{', code)
if not wi_match:
    print('FAIL: WorkItem struct not found')
    sys.exit(1)
body = code[wi_match.start():wi_match.start()+1500]
if 'path' not in body:
    print('FAIL: WorkItem missing path field')
    sys.exit(1)
if 'Kind' not in body and 'kind' not in body:
    print('FAIL: WorkItem missing kind field/type')
    sys.exit(1)
print('PASS: WorkItem retains path and kind')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): WorkItem retains path and kind"
else
    add_total 0.05
    echo "FAIL (0.05): WorkItem retains path and kind"
fi

##############################################################################
# ANTI-STUB (0.15 total)
# Verify the fix is substantial code, not keyword injection or stub functions.
##############################################################################

# [pr_diff] (0.10): GlobWalker.zig has substantial modifications (>=30 added lines)
python3 -c "
import subprocess, sys
result = subprocess.run(
    ['git', 'diff', '--numstat', 'HEAD', '--', 'src/glob/GlobWalker.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
if result.returncode != 0 or not result.stdout.strip():
    print('FAIL: No changes to GlobWalker.zig')
    sys.exit(1)
parts = result.stdout.strip().split()
added, deleted = int(parts[0]), int(parts[1])
if added < 30:
    print(f'FAIL: Only {added} lines added (need >=30 for a real fix)')
    sys.exit(1)
if added < deleted * 0.3:
    print(f'FAIL: {added} added vs {deleted} deleted — looks like mostly deletions')
    sys.exit(1)
print(f'PASS: Substantial modification ({added} added, {deleted} deleted)')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS (0.10): Substantial code modification"
else
    add_total 0.10
    echo "FAIL (0.10): Substantial code modification"
fi

# [pr_diff] (0.05): At least 2 new function definitions added to GlobWalker.zig
python3 -c "
import subprocess, re, sys
result = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/glob/GlobWalker.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
diff = result.stdout
new_fns = re.findall(r'^\+\s+(?:pub\s+)?(?:inline\s+)?fn\s+(\w+)', diff, re.MULTILINE)
if len(new_fns) < 2:
    print(f'FAIL: Only {len(new_fns)} new functions (need >=2)')
    sys.exit(1)
print(f'PASS: {len(new_fns)} new functions: {new_fns[:5]}')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): New helper functions added"
else
    add_total 0.05
    echo "FAIL (0.05): New helper functions added"
fi

##############################################################################
# CONFIG-DERIVED (0.10 total)
##############################################################################

# [agent_config] (0.05): "Memory management — be careful with allocators" — CLAUDE.md:232 @ 3ca678c9
# New code must use allocator for any heap-backed collection.
python3 -c "
import subprocess, sys
result = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/glob/GlobWalker.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
added = [l[1:] for l in result.stdout.split('\n') if l.startswith('+') and not l.startswith('+++')]
text = '\n'.join(added)
if 'allocator' not in text:
    print('FAIL: New code does not reference any allocator')
    sys.exit(1)
print('PASS: New code uses allocator for memory management')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): Memory management with allocator"
else
    add_total 0.05
    echo "FAIL (0.05): Memory management with allocator"
fi

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:228 @ 3ca678c9
# New functions should be GlobWalker methods (take this/self as first param).
python3 -c "
import subprocess, re, sys
result = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/glob/GlobWalker.zig'],
    capture_output=True, text=True, cwd='/workspace/bun'
)
new_fn_lines = re.findall(r'^\+\s+(?:pub\s+)?(?:inline\s+)?fn\s+\w+\s*\(([^)]*)', result.stdout, re.MULTILINE)
if not new_fn_lines:
    print('FAIL: No new function definitions found in diff')
    sys.exit(1)
method_count = sum(1 for p in new_fn_lines if 'this' in p or 'self' in p)
if method_count < 1:
    print('FAIL: No new methods follow GlobWalker convention (this/self param)')
    sys.exit(1)
print(f'PASS: {method_count}/{len(new_fn_lines)} new functions are GlobWalker methods')
" 2>/dev/null
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS (0.05): New functions follow existing code style"
else
    add_total 0.05
    echo "FAIL (0.05): New functions follow existing code style"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo "Total: $SCORE / $TOTAL"

REWARD=$(python3 -c "
total = $TOTAL
score = $SCORE
reward = round(score / total, 4) if total > 0 else 0.0
print(reward)
")

echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
total = $TOTAL
score = $SCORE
reward = round(score / total, 4) if total > 0 else 0.0
# F2P structural (0.35) + Core fix (0.25) = behavioral-equivalent
behavioral = min(0.60, score)
remainder = max(0, score - 0.60)
# Regression (0.15)
regression = min(0.15, remainder)
remainder = max(0, remainder - 0.15)
# Anti-stub + config (0.25)
config = min(0.25, remainder)
print(json.dumps({
    'reward': reward,
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
