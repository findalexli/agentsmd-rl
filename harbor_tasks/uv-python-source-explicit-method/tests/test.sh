#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0
DETAILS=""

add_check() {
    local name="$1" weight="$2" pass="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        EARNED=$(python3 -c "print($EARNED + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $name\n"
    fi
}

cd /repo

FILE="crates/uv-python/src/discovery.rs"

# ============================================================
# GATE: File must exist and be non-empty
# ============================================================
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE is missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

# ============================================================
# [pr_diff] (0.35): is_explicit() method on PythonSource returns correct values
# WHY structural: Rust code — no cargo/rustc in Docker image
# Accepts both self and &self, both match and matches! patterns
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

# Find is_explicit method — accept both self and &self
method_match = re.search(
    r'fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{',
    src
)
if not method_match:
    print('FAIL: is_explicit(&?self) -> bool method not found')
    sys.exit(1)

# Extract method body — find matching closing brace
start = method_match.end()
depth = 1
i = start
while i < len(src) and depth > 0:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]

# Check all 11 variants are mentioned in the body
explicit = ['ProvidedPath', 'ParentInterpreter', 'ActiveEnvironment', 'CondaPrefix']
non_explicit = ['Managed', 'DiscoveredEnvironment', 'SearchPath', 'SearchPathFirst',
                'Registry', 'MicrosoftStore', 'BaseCondaPrefix']

missing = []
for v in explicit + non_explicit:
    if v not in body:
        missing.append(v)

if missing:
    print(f'FAIL: is_explicit missing variants: {missing}')
    sys.exit(1)

# Verify explicit variants map to true and non-explicit to false
# Strategy: find which variants are in the true-producing context
# Works for both 'match self { ... => true, ... => false }' and 'matches!(self, ...)'

# For match-style: find true arm and false arm
true_arm = re.search(r'((?:(?:Self|PythonSource)::\w+\s*\|?\s*)+)\s*=>\s*true', body, re.DOTALL)
false_arm = re.search(r'((?:(?:Self|PythonSource)::\w+\s*\|?\s*)+)\s*=>\s*false', body, re.DOTALL)

# For matches!-style: the listed variants produce true, unlisted produce false
matches_call = re.search(r'matches!\s*\(\s*self\s*,\s*(.*?)\)', body, re.DOTALL)

ok = True
if true_arm and false_arm:
    true_text = true_arm.group(1)
    false_text = false_arm.group(1)
    for v in explicit:
        if v not in true_text:
            print(f'FAIL: {v} should be explicit (true) but is not in true arm')
            ok = False
    for v in non_explicit:
        if v not in false_text:
            # Could be using wildcard _ => false, which is valid
            if '_' not in body or re.search(r'_\s*=>\s*false', body):
                pass  # wildcard catches it
            else:
                print(f'FAIL: {v} should be non-explicit (false) but is not in false arm')
                ok = False
elif matches_call:
    # matches! lists the true variants; everything else is false
    matched_text = matches_call.group(1)
    for v in explicit:
        if v not in matched_text:
            print(f'FAIL: {v} should be in matches! (explicit) but is not')
            ok = False
    for v in non_explicit:
        if v in matched_text:
            print(f'FAIL: {v} should NOT be in matches! (non-explicit) but is')
            ok = False
else:
    # Check for negated matches! — matches!(self, ...) with non-explicit returning !
    neg_matches = re.search(r'!\s*matches!\s*\(\s*self\s*,\s*(.*?)\)', body, re.DOTALL)
    if neg_matches:
        # !matches! lists non-explicit variants (returns true when NOT matching)
        matched_text = neg_matches.group(1)
        for v in non_explicit:
            if v not in matched_text:
                print(f'FAIL: {v} should be in negated matches! but is not')
                ok = False
        for v in explicit:
            if v in matched_text:
                print(f'FAIL: {v} should NOT be in negated matches! but is')
                ok = False
    else:
        print('FAIL: Could not parse is_explicit return logic (no match/matches! found)')
        ok = False

if ok:
    print('PASS: is_explicit method with correct variant mapping')
    sys.exit(0)
else:
    sys.exit(1)
" && PASS_CORE=1 || PASS_CORE=0
add_check "[pr_diff] is_explicit() method with correct variant mapping" 0.35 "$PASS_CORE"

# ============================================================
# [pr_diff] (0.25): allows_installation calls source.is_explicit() and inline match removed
# WHY structural: Rust code — no cargo/rustc in Docker image
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

# Find the allows_installation method
method_match = re.search(
    r'fn\s+allows_installation\s*\(self.*?\{',
    src
)
if not method_match:
    print('FAIL: Could not find allows_installation method')
    sys.exit(1)

# Extract body (brace-matched)
start = method_match.end()
depth = 1
i = start
while i < len(src) and depth > 0:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]

# Must call .is_explicit() somewhere in the body
if '.is_explicit()' not in body:
    print('FAIL: allows_installation does not call .is_explicit()')
    sys.exit(1)

# Must NOT have the old inline match pattern
if re.search(r'let\s+is_explicit\s*=\s*match\s+', body):
    print('FAIL: Still has inline let is_explicit = match in allows_installation')
    sys.exit(1)

print('PASS: allows_installation delegates to .is_explicit() and inline match removed')
sys.exit(0)
" && PASS_REFACTOR=1 || PASS_REFACTOR=0
add_check "[pr_diff] allows_installation delegates to is_explicit(), inline match removed" 0.25 "$PASS_REFACTOR"

# ============================================================
# [pr_diff] (0.15): Anti-stub — is_explicit has substantive match logic
# WHY structural: Rust code — no cargo/rustc in Docker image
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

# Find is_explicit method body
method_match = re.search(
    r'fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{',
    src
)
if not method_match:
    print('FAIL: No is_explicit method found')
    sys.exit(1)

start = method_match.end()
depth = 1
i = start
while i < len(src) and depth > 0:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]

# Must have match or matches! (not just 'true' or 'false')
has_match = 'match' in body or 'matches!' in body
# Must reference at least 8 distinct variants via Self:: or PythonSource::
variant_refs = set(re.findall(r'(?:Self|PythonSource)::(\w+)', body))
# Body must have at least 3 non-whitespace lines
lines = [l.strip() for l in body.strip().splitlines() if l.strip()]

if not has_match:
    print('FAIL: is_explicit has no match/matches! expression')
    sys.exit(1)
if len(variant_refs) < 8:
    print(f'FAIL: is_explicit references only {len(variant_refs)} variants (need >=8)')
    sys.exit(1)
if len(lines) < 3:
    print(f'FAIL: is_explicit body too short ({len(lines)} lines)')
    sys.exit(1)

print(f'PASS: is_explicit has match with {len(variant_refs)} variants, {len(lines)} lines')
sys.exit(0)
" && PASS_ANTISTUB=1 || PASS_ANTISTUB=0
add_check "[pr_diff] Anti-stub: is_explicit has real match logic" 0.15 "$PASS_ANTISTUB"

# ============================================================
# [repo_tests] (0.10): Pass-to-pass — is_maybe_system method still exists
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

if re.search(r'fn\s+is_maybe_system\s*\(\s*&?\s*self\s*\)\s*->\s*bool', src):
    print('PASS: is_maybe_system method still exists')
    sys.exit(0)
else:
    print('FAIL: is_maybe_system method missing — regression')
    sys.exit(1)
" && PASS_P2P=1 || PASS_P2P=0
add_check "[repo_tests] is_maybe_system method still exists" 0.10 "$PASS_P2P"

# ============================================================
# [pr_diff] (0.10): SearchPathFirst variant is handled in is_explicit
# WHY: Gold patch and instruction both list SearchPathFirst as non-explicit
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

# Find is_explicit method body
method_match = re.search(
    r'fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{',
    src
)
if not method_match:
    print('FAIL: No is_explicit method found')
    sys.exit(1)

start = method_match.end()
depth = 1
i = start
while i < len(src) and depth > 0:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]

if 'SearchPathFirst' in body:
    print('PASS: SearchPathFirst variant handled in is_explicit')
    sys.exit(0)
else:
    print('FAIL: SearchPathFirst not handled in is_explicit')
    sys.exit(1)
" && PASS_SPF=1 || PASS_SPF=0
add_check "[pr_diff] SearchPathFirst variant handled in is_explicit" 0.10 "$PASS_SPF"

# ============================================================
# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:7 @ d7da792
# ============================================================
python3 -c "
import re, sys

with open('$FILE') as f:
    src = f.read()

method_match = re.search(
    r'fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{',
    src
)
if method_match:
    start = method_match.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{': depth += 1
        elif src[i] == '}': depth -= 1
        i += 1
    body = src[start:i-1]
    for bad in ['.unwrap()', 'panic!', 'unreachable!', 'unsafe']:
        if bad in body:
            print(f'FAIL: is_explicit contains {bad}')
            sys.exit(1)

print('PASS: No unwrap/panic/unreachable in is_explicit')
sys.exit(0)
" && PASS_CONFIG=1 || PASS_CONFIG=0
add_check "[agent_config] No unwrap/panic/unreachable in is_explicit — CLAUDE.md:7" 0.05 "$PASS_CONFIG"

# ============================================================
# Compute final reward
# ============================================================
REWARD=$(python3 -c "print(round($EARNED, 2))")
echo -e "\n=== Results ==="
echo -e "$DETAILS"
echo "Total: $EARNED / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

# Write reward.json
python3 -c "
import json
reward = $REWARD
behavioral = round($PASS_CORE * 0.35 + $PASS_REFACTOR * 0.25 + $PASS_ANTISTUB * 0.15 + $PASS_SPF * 0.10, 2)
regression = round($PASS_P2P * 0.10, 2)
config = round($PASS_CONFIG * 0.05, 2)
print(json.dumps({
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
