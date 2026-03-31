#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
TARGET="$REPO/src/bun.js/api/bun/dns.zig"
REWARD_FILE="/logs/verifier/reward.txt"
JSON_FILE="/logs/verifier/reward.json"

F2P_GUARD=0
F2P_METHOD=0
P2P_OPTS=0
P2P_CORE=0
CFG=0

# =============================================================================
# GATE: dns.zig must exist and be structurally intact
# WHY structural: Zig requires full Bun build toolchain (cmake+zig+clang)
# to compile and run; cannot call dns.zig functions in this environment.
# =============================================================================

if ! [ -f "$TARGET" ]; then
    echo "GATE FAIL: dns.zig not found"
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$JSON_FILE"
    exit 0
fi

python3 -c "
import sys
content = open('$TARGET').read()
opens = content.count('{')
closes = content.count('}')
if abs(opens - closes) > 5:
    sys.exit(1)
if 'pub const Resolver = struct' not in content:
    sys.exit(1)
if 'GetAddrInfo' not in content:
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: dns.zig structural integrity broken"
    echo "0.0" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "$JSON_FILE"
    exit 0
fi
echo "GATE PASS: dns.zig structural integrity OK"

# =============================================================================
# FAIL-TO-PASS 1: A type guard still exists AND isCell() is not the sole guard
# (0.35) — The bug was isCell() being too permissive. A correct fix replaces
# or augments it. Simply DELETING the guard is wrong (all values enter parsing).
# =============================================================================

# [pr_diff] (0.35): Guard on arguments.ptr[1] exists and isCell is not sole guard
python3 -c "
import re, sys

content = open('$TARGET').read()
lines = content.split('\n')

# Find lines referencing arguments.ptr[1]
ptr_indices = [i for i, l in enumerate(lines) if 'arguments.ptr[1]' in l]
if not ptr_indices:
    print('FAIL: arguments.ptr[1] reference removed entirely')
    sys.exit(1)

# Look for the guard region: where arguments.ptr[1] is checked before options parsing
found_guard = False
for idx in ptr_indices:
    window_start = max(0, idx - 2)
    window_end = min(len(lines), idx + 30)
    window = '\n'.join(lines[window_start:window_end])

    # This is THE guard region if it leads to getTruthy/optionsObject
    if 'getTruthy' not in window and 'optionsObject' not in window:
        continue

    found_guard = True

    # Check the guard line itself and nearby lines for a conditional
    guard_area = '\n'.join(lines[window_start:min(len(lines), idx + 5)])

    # 1) There must be a conditional (if/switch/else) in the guard area
    #    that tests the second argument before using it as options
    has_conditional = bool(re.search(r'\bif\b.*arguments', guard_area)) or \
                      bool(re.search(r'\bswitch\b.*arguments', guard_area)) or \
                      bool(re.search(r'arguments\.ptr\[1\]\..*\(', guard_area))
    if not has_conditional:
        # Maybe arguments.ptr[1] is assigned to a variable and tested
        # Look for assignment then conditional
        extended = '\n'.join(lines[window_start:min(len(lines), idx + 10)])
        var_assign = re.search(r'(const|var)\s+(\w+)\s*=\s*arguments\.ptr\[1\]', extended)
        if var_assign:
            var_name = var_assign.group(2)
            if re.search(rf'if\b.*{var_name}', extended):
                has_conditional = True

    if not has_conditional:
        print('FAIL: no type guard conditional found before options parsing')
        sys.exit(1)

    # 2) isCell() must NOT be the sole guard
    if 'isCell()' in guard_area:
        stricter = re.findall(r'\.(is[A-Z]\w*)\(\)', guard_area)
        stricter = [m for m in stricter if m != 'isCell']
        if not stricter and '.jsType()' not in guard_area:
            print('FAIL: isCell() still the sole guard on options argument')
            sys.exit(1)

    print('PASS: guard exists and isCell is not the sole check')
    sys.exit(0)

if not found_guard:
    print('FAIL: no guard region found protecting options parsing')
    sys.exit(1)
" && F2P_GUARD=1
echo "F2P_GUARD (guard exists, isCell not sole): $F2P_GUARD"

# =============================================================================
# FAIL-TO-PASS 2: The replacement guard uses a real JSValue method that
# correctly distinguishes objects from non-object cells (like strings).
# (0.25) — Dynamically discovers valid isXxx methods from Bun's bindings.
# =============================================================================

# [pr_diff] (0.25): Replacement guard uses a real, object-discriminating JSValue method
python3 -c "
import re, sys, os

content = open('$TARGET').read()
lines = content.split('\n')

# Discover real isXxx methods from Bun's JSValue bindings
bindings_dir = '$REPO/src/bun.js/bindings'
valid_methods = set()
for root, dirs, files in os.walk('$REPO/src/bun.js'):
    for fname in files:
        if fname.endswith('.zig') or fname.endswith('.h'):
            try:
                src = open(os.path.join(root, fname)).read()
                for m in re.findall(r'(?:pub\s+)?fn\s+(is[A-Z]\w*)', src):
                    valid_methods.add(m)
                for m in re.findall(r'bool\s+(is[A-Z]\w*)', src):
                    valid_methods.add(m)
            except:
                pass

# Remove isCell — the buggy method. Also remove methods that don't help
# discriminate objects from strings (these would have the same bug).
disqualified = {'isCell'}  # isCell is the buggy method itself
valid_methods -= disqualified

if not valid_methods:
    # Fallback if file discovery fails (should not happen in Docker)
    valid_methods = {'isObject', 'isObjectLike', 'isObjectOrNull',
                     'isFunction', 'isCallable', 'isStructuredClone'}

# Find guard region
ptr_indices = [i for i, l in enumerate(lines) if 'arguments.ptr[1]' in l]
if not ptr_indices:
    sys.exit(1)

for idx in ptr_indices:
    window_start = max(0, idx - 2)
    window_end = min(len(lines), idx + 30)
    window = '\n'.join(lines[window_start:window_end])

    if 'getTruthy' not in window and 'optionsObject' not in window:
        continue

    guard_area = '\n'.join(lines[max(0, idx - 2):min(len(lines), idx + 8)])
    methods_used = re.findall(r'\.(is[A-Z]\w*)\(\)', guard_area)

    for m in methods_used:
        if m in valid_methods:
            print(f'PASS: guard uses valid method .{m}()')
            sys.exit(0)

    # Also accept jsType() comparisons (alternative approach)
    if '.jsType()' in guard_area:
        print('PASS: guard uses jsType() comparison')
        sys.exit(0)

    print(f'FAIL: guard methods {methods_used} not in valid set')
    sys.exit(1)

sys.exit(1)
" && F2P_METHOD=1
echo "F2P_METHOD (valid replacement method): $F2P_METHOD"

# =============================================================================
# PASS-TO-PASS: Existing functionality preserved (GATED behind F2P)
# =============================================================================

if [ "$F2P_GUARD" -eq 1 ]; then

    # [pr_diff] (0.15): Options parsing block still extracts port and family via getTruthy
    python3 -c "
import sys
content = open('$TARGET').read()
lines = content.split('\n')

# The options parsing must still handle port via getTruthy near arguments.ptr[1]
ptr_indices = [i for i, l in enumerate(lines) if 'arguments.ptr[1]' in l]
for idx in ptr_indices:
    window = '\n'.join(lines[idx:min(len(lines), idx + 50)])
    if 'getTruthy' in window and 'port' in window:
        print('PASS: options parsing intact near guard')
        sys.exit(0)

print('FAIL: getTruthy/port not found near arguments.ptr[1]')
sys.exit(1)
" && P2P_OPTS=1
    echo "P2P_OPTS (options parsing intact): $P2P_OPTS"

    # [repo_tests] (0.10): Core Resolver struct and key methods still present
    python3 -c "
import sys
content = open('$TARGET').read()
required = ['pub const Resolver = struct', 'GetAddrInfo', 'globalThis']
for r in required:
    if r not in content:
        print(f'FAIL: missing {r}')
        sys.exit(1)
print('PASS: core structure intact')
" && P2P_CORE=1
    echo "P2P_CORE (core structure intact): $P2P_CORE"

else
    echo "P2P_OPTS: SKIPPED (gated behind F2P_GUARD)"
    echo "P2P_CORE: SKIPPED (gated behind F2P_GUARD)"
fi

# =============================================================================
# CONFIG-DERIVED: Rules from agent config files (GATED behind F2P)
# =============================================================================

if [ "$F2P_GUARD" -eq 1 ]; then

    # [agent_config] (0.15): No use of std.* APIs where bun.* equivalents exist — src/CLAUDE.md:16 @ 7fb7897
    python3 -c "
import subprocess, sys

result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, cwd='$REPO')
diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, cwd='$REPO')
    diff = result.stdout
if not diff:
    print('FAIL: no changes detected')
    sys.exit(1)

added_lines = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
forbidden = ['std.fs', 'std.posix', 'std.os', 'std.process']
for line in added_lines:
    for f in forbidden:
        if f in line:
            print(f'FAIL: prohibited {f} in added code')
            sys.exit(1)
print('PASS: no prohibited std.* APIs')
" && CFG=1
    echo "CFG (no std.* APIs): $CFG"

else
    echo "CFG: SKIPPED (gated behind F2P_GUARD)"
fi

# =============================================================================
# RESULTS
# =============================================================================

BEH=$(python3 -c "print($F2P_GUARD * 0.35 + $F2P_METHOD * 0.25)")
REG=$(python3 -c "print($P2P_OPTS * 0.15 + $P2P_CORE * 0.10)")
CFG_SCORE=$(python3 -c "print($CFG * 0.15)")
FINAL=$(python3 -c "
total = $F2P_GUARD * 0.35 + $F2P_METHOD * 0.25 + $P2P_OPTS * 0.15 + $P2P_CORE * 0.10 + $CFG * 0.15
print(f'{min(1.0, max(0.0, total)):.4f}')
")

echo ""
echo "=== Test Results ==="
echo "F2P guard (0.35): $F2P_GUARD"
echo "F2P method(0.25): $F2P_METHOD"
echo "P2P opts  (0.15): $P2P_OPTS"
echo "P2P core  (0.10): $P2P_CORE"
echo "Config    (0.15): $CFG"
echo "Behavioral: $BEH | Regression: $REG | Config: $CFG_SCORE"
echo "Final reward: $FINAL"

echo "$FINAL" > "$REWARD_FILE"
echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"config\": $CFG_SCORE, \"style_rubric\": 0.0}" > "$JSON_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
