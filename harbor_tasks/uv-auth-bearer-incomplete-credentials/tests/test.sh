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

# ============================================================
# GATE: Syntax check — file must parse as valid Rust
# ============================================================
if ! python3 -c "
import subprocess, sys
result = subprocess.run(['rustfmt', '--check', 'crates/uv-auth/src/middleware.rs'],
                       capture_output=True, timeout=30)
sys.exit(0 if result.returncode in (0, 1) else 1)
"; then
    echo "GATE FAILED: middleware.rs has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
    exit 0
fi

# ============================================================
# [pr_diff] (0.35): Auth policy guard uses is_authenticated() instead of password().is_none()
# Behavioral-equivalent: verifies the guard EXISTS and uses the correct method.
# Accepts any structure (matches!, match, if-let, ==) as long as
# is_authenticated() is used in the auth_policy + Always guard context.
# ============================================================
python3 -c "
import re, sys

with open('crates/uv-auth/src/middleware.rs') as f:
    lines = f.readlines()

# Strip single-line comments to prevent comment injection gaming
stripped = []
for line in lines:
    code = line.split('//')[0] if '//' in line else line
    stripped.append(code)
src = ''.join(stripped)

# 1) The file must contain is_authenticated() in actual code (not comments)
if 'is_authenticated()' not in src:
    print('FAIL: is_authenticated() not found in code (excluding comments)')
    sys.exit(1)

# 2) There must be an auth policy guard that returns an error for incomplete creds.
#    Accept any form: matches!, match, if, == etc. Just need AuthPolicy::Always
#    and is_authenticated() to appear within 8 lines of each other, in code.
found_guard = False
for i, line in enumerate(stripped):
    if 'AuthPolicy::Always' in line:
        # Check surrounding window (i-3 to i+8) for is_authenticated()
        window = ''.join(stripped[max(0,i-3):i+8])
        if 'is_authenticated()' in window:
            found_guard = True
            break

if not found_guard:
    print('FAIL: No auth policy guard using is_authenticated() found')
    sys.exit(1)

# 3) The guard must return an Err (not just check and do nothing)
err_near_guard = False
for i, line in enumerate(stripped):
    if 'AuthPolicy::Always' in line:
        window = ''.join(stripped[max(0,i-1):i+8])
        if 'is_authenticated()' in window and ('Err(' in window or 'return Err' in window):
            err_near_guard = True
            break

if not err_near_guard:
    print('FAIL: Auth guard with is_authenticated() does not return an error')
    sys.exit(1)

print('PASS: Auth policy guard correctly uses is_authenticated() and returns Err')
sys.exit(0)
" && CHK1=1 || CHK1=0
add_check "[pr_diff] Auth policy guard uses is_authenticated() with Err return" 0.35 "$CHK1"

# ============================================================
# [pr_diff] (0.25): Buggy pattern password().is_none() removed from auth guard
# Must verify the OLD buggy pattern is gone from actual code (not comments).
# Also verifies the guard wasn't simply DELETED (anti-deletion check).
# ============================================================
python3 -c "
import re, sys

with open('crates/uv-auth/src/middleware.rs') as f:
    lines = f.readlines()

# Strip comments
stripped = []
for line in lines:
    code = line.split('//')[0] if '//' in line else line
    stripped.append(code)
src_no_comments = ''.join(stripped)

# Check that password().is_none() is NOT used in auth policy context
for i, line in enumerate(stripped):
    if 'AuthPolicy::Always' in line:
        window = ''.join(stripped[max(0,i-2):i+6])
        if 'password()' in window and 'is_none()' in window:
            print('FAIL: Auth policy guard still uses password().is_none()')
            sys.exit(1)

# Anti-deletion: AuthPolicy::Always must still appear in code (guard wasn't deleted)
if 'AuthPolicy::Always' not in src_no_comments:
    print('FAIL: AuthPolicy::Always guard was deleted instead of fixed')
    sys.exit(1)

print('PASS: Buggy password().is_none() pattern removed, guard still exists')
sys.exit(0)
" && CHK2=1 || CHK2=0
add_check "[pr_diff] Buggy password().is_none() removed, guard preserved" 0.25 "$CHK2"

# ============================================================
# [pr_diff] (0.10): Error message no longer says 'Missing password'
# The error was misleading for Bearer tokens — should be more generic.
# Accepts ANY message that doesn't say 'Missing password'.
# ============================================================
python3 -c "
import sys

with open('crates/uv-auth/src/middleware.rs') as f:
    lines = f.readlines()

# Check actual code, not comments
for line in lines:
    code = line.split('//')[0] if '//' in line else line
    if 'Missing password' in code:
        print('FAIL: Code still contains misleading Missing password error')
        sys.exit(1)

# Verify there IS an error message near the auth guard (wasn't just deleted)
src = ''.join(lines)
import re
if not re.search(r'format_err!\s*\(', src):
    print('FAIL: No format_err! found — error handling may have been deleted')
    sys.exit(1)

print('PASS: Missing password error removed, error handling preserved')
sys.exit(0)
" && CHK3=1 || CHK3=0
add_check "[pr_diff] Error message no longer says Missing password" 0.10 "$CHK3"

# ============================================================
# [pr_diff] (0.10): Comment/trace in complete_request_with_request_credentials updated
# The instruction mentions this secondary fix: comments/trace messages that say
# 'username and password' should be updated to reflect Bearer auth support.
# ============================================================
python3 -c "
import sys

with open('crates/uv-auth/src/middleware.rs') as f:
    src = f.read()

# The old trace/comment said 'username and password' — this is misleading
# because the code handles Bearer tokens too. Check it's been updated.
if 'username and password' in src:
    print('FAIL: Still references username and password in trace/comments')
    sys.exit(1)

print('PASS: No longer references username and password')
sys.exit(0)
" && CHK4=1 || CHK4=0
add_check "[pr_diff] Trace/comments updated from username and password" 0.10 "$CHK4"

# ============================================================
# [repo_tests] (0.10): Pass-to-pass — edit.rs error message consistency
# If the error message changed in middleware.rs, the test file should match.
# ============================================================
python3 -c "
import sys, re

with open('crates/uv-auth/src/middleware.rs') as f:
    middleware = f.read()

# Extract error string from format_err! near AuthPolicy::Always
lines = middleware.split('\n')
error_region = ''
for i, line in enumerate(lines):
    if 'AuthPolicy::Always' in line:
        error_region = '\n'.join(lines[i:i+10])
        break

m = re.search(r'format_err!\s*\(\s*\"([^\"]+)\"', error_region)
if not m:
    # Try multiline format_err
    m = re.search(r'format_err!\s*\(\s*\n\s*\"([^\"]+)\"', error_region)

if m:
    # Get the static part of the error message (before any {})
    msg_fragment = m.group(1).split('{')[0].strip()
    if len(msg_fragment) < 3:
        print('SKIP: Error message fragment too short to match')
        sys.exit(1)

    with open('crates/uv/tests/it/edit.rs') as f:
        test_src = f.read()

    if msg_fragment in test_src:
        print(f'PASS: edit.rs contains matching error fragment: {msg_fragment!r}')
        sys.exit(0)
    else:
        print(f'FAIL: edit.rs does not contain error fragment: {msg_fragment!r}')
        sys.exit(1)
else:
    print('SKIP: Could not extract error message from auth guard region')
    sys.exit(1)
" && CHK5=1 || CHK5=0
add_check "[repo_tests] edit.rs error message matches middleware.rs" 0.10 "$CHK5"

# ============================================================
# [agent_config] (0.05): No unwrap/panic near auth policy guard — CLAUDE.md:7
# ============================================================
python3 -c "
import sys

with open('crates/uv-auth/src/middleware.rs') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'AuthPolicy::Always' in line:
        region = lines[max(0,i-2):i+8]
        for rline in region:
            code = rline.split('//')[0]
            if '.unwrap()' in code or 'panic!' in code or 'unreachable!' in code:
                print(f'FAIL: Found unwrap/panic/unreachable near auth guard: {rline.strip()}')
                sys.exit(1)

print('PASS: No unwrap/panic/unreachable near auth policy guard')
sys.exit(0)
" && CHK6=1 || CHK6=0
add_check "[agent_config] No unwrap/panic near auth guard — CLAUDE.md:7" 0.05 "$CHK6"

# ============================================================
# [pr_diff] (0.05): Anti-stub — meaningful changes in complete_request function
# The function must have is_authenticated() in code AND no password().is_none()
# AND the guard returns an error — ensures real logic, not stubs.
# ============================================================
python3 -c "
import sys

with open('crates/uv-auth/src/middleware.rs') as f:
    lines = f.readlines()

# Strip comments
code_lines = []
for line in lines:
    code = line.split('//')[0] if '//' in line else line
    code_lines.append(code)
src = ''.join(code_lines)

checks = 0
# Must have is_authenticated() in code
if 'is_authenticated()' in src:
    checks += 1
# Must NOT have password().is_none() near AuthPolicy::Always
has_buggy_guard = False
for i, line in enumerate(code_lines):
    if 'AuthPolicy::Always' in line:
        window = ''.join(code_lines[max(0,i-2):i+6])
        if 'password()' in window:
            has_buggy_guard = True
if not has_buggy_guard:
    checks += 1
# Must have an Err return in the guard
for i, line in enumerate(code_lines):
    if 'AuthPolicy::Always' in line:
        window = ''.join(code_lines[max(0,i-1):i+8])
        if 'Err(' in window:
            checks += 1
            break

if checks >= 3:
    print('PASS: Real logic change, not a stub')
    sys.exit(0)
else:
    print(f'FAIL: Only {checks}/3 anti-stub criteria met')
    sys.exit(1)
" && CHK7=1 || CHK7=0
add_check "[pr_diff] Anti-stub: meaningful logic change verified" 0.05 "$CHK7"

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
behavioral = round($CHK1 * 0.35 + $CHK2 * 0.25 + $CHK3 * 0.10 + $CHK4 * 0.10, 2)
regression = round($CHK5 * 0.10, 2)
config = round($CHK6 * 0.05, 2)
print(json.dumps({
    'reward': $REWARD,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
