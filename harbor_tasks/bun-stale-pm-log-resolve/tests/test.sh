#!/usr/bin/env bash
set +e

TOTAL=0
PASS=0
GATE_PASS=true

cd /workspace/bun

TARGET="src/bun.js/VirtualMachine.zig"

##############################################################################
# GATE: VirtualMachine.zig exists and contains resolveMaybeNeedsTrailingSlash
##############################################################################
# [pr_diff] (gate): Target file must exist and contain the function
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    GATE_PASS=false
elif ! grep -q 'pub fn resolveMaybeNeedsTrailingSlash' "$TARGET" 2>/dev/null; then
    echo "GATE FAIL: resolveMaybeNeedsTrailingSlash not found in $TARGET"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: target file and function exist"

##############################################################################
# Helper: extract function body with comments stripped
# WHY STRUCTURAL: Zig requires full bun build toolchain (cmake, zig compiler,
# WebKit) — cannot compile or call the code in this container.
##############################################################################

# Extract the function body (from signature to closing brace at indent level 4)
FUNC_BODY=$(sed -n '/pub fn resolveMaybeNeedsTrailingSlash/,/^    }/p' "$TARGET")

# Strip single-line comments for all checks (prevent comment-injection gaming)
FUNC_BODY_NOCOMMENT=$(echo "$FUNC_BODY" | sed 's|//.*||')

# Extract the defer block (also comment-stripped)
DEFER_BODY=$(echo "$FUNC_BODY_NOCOMMENT" | sed -n '/defer {/,/}/p')

##############################################################################
# Fail-to-pass: Core bug fix checks (0.55 total)
# These are structural checks on Zig source (can't compile). Hardened against
# comment injection and accepting multiple valid Zig syntaxes.
##############################################################################

# [pr_diff] (0.30): package_manager log is set to &log in resolveMaybeNeedsTrailingSlash
# Accepts both |pm| capture and .? optional access syntax
# Must appear in the non-defer part of the function (before resolve call)
BEFORE_DEFER=$(echo "$FUNC_BODY_NOCOMMENT" | sed -n '1,/defer {/p')

PM_SET=false
# Pattern 1: if (....package_manager) |pm| { ... pm.log = &log ... }
if echo "$BEFORE_DEFER" | grep -q 'package_manager' && \
   echo "$BEFORE_DEFER" | grep -q '\.log = &log'; then
    # Verify it's the package_manager's log, not just any .log = &log
    # (resolver.log and linker.log already exist in the original code)
    # Check that package_manager appears near a .log assignment
    if echo "$BEFORE_DEFER" | grep 'package_manager' | grep -q 'log' || \
       echo "$BEFORE_DEFER" | python3 -c "
import sys
lines = sys.stdin.read()
# Look for package_manager access followed by .log = &log within 3 lines
pm_lines = []
all_lines = lines.splitlines()
for i, line in enumerate(all_lines):
    if 'package_manager' in line:
        pm_lines.append(i)
for pm_i in pm_lines:
    for j in range(pm_i, min(pm_i + 4, len(all_lines))):
        if '.log = &log' in all_lines[j] or '.log=&log' in all_lines[j]:
            sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
        PM_SET=true
    fi
fi

if [ "$PM_SET" = true ]; then
    echo "PASS (0.30): package_manager log set to &log before resolve call"
    PASS=$((PASS + 30))
else
    echo "FAIL (0.30): package_manager log NOT set to &log before resolve call"
fi

# [pr_diff] (0.25): package_manager log is restored in the defer block
# The defer must restore pm.log so the pointer doesn't dangle after return
PM_RESTORE=false
if echo "$DEFER_BODY" | grep -q 'package_manager' && \
   echo "$DEFER_BODY" | grep -q '\.log = old_log\|\.log=old_log'; then
    # Verify package_manager's log is being restored (not just any .log)
    if echo "$DEFER_BODY" | grep 'package_manager' | grep -q 'log' || \
       echo "$DEFER_BODY" | python3 -c "
import sys
lines = sys.stdin.read()
all_lines = lines.splitlines()
pm_lines = []
for i, line in enumerate(all_lines):
    if 'package_manager' in line:
        pm_lines.append(i)
for pm_i in pm_lines:
    for j in range(pm_i, min(pm_i + 4, len(all_lines))):
        if 'old_log' in all_lines[j] and '.log' in all_lines[j]:
            sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
        PM_RESTORE=true
    fi
fi

if [ "$PM_RESTORE" = true ]; then
    echo "PASS (0.25): package_manager log restored in defer block"
    PASS=$((PASS + 25))
else
    echo "FAIL (0.25): package_manager log NOT restored in defer block"
fi

##############################################################################
# Anti-stub: The function must not be gutted (0.10)
##############################################################################
# [pr_diff] (0.10): Function body has substantive content (anti-stub)
# The original function has ~30+ lines; a stub or near-empty body is gaming
STMT_COUNT=$(echo "$FUNC_BODY_NOCOMMENT" | grep -c '[a-zA-Z_]' 2>/dev/null || echo 0)
if [ "$STMT_COUNT" -ge 15 ]; then
    echo "PASS (0.10): Function body has $STMT_COUNT substantive lines (anti-stub)"
    PASS=$((PASS + 10))
else
    echo "FAIL (0.10): Function body only has $STMT_COUNT lines — likely stubbed"
fi

##############################################################################
# Pass-to-pass: Existing functionality not broken (0.15)
##############################################################################

# [pr_diff] (0.10): Original resolver/linker log save/restore still intact
# These lines existed before the fix and must not be removed
P2P_OK=true
for pattern in \
    'transpiler\.resolver\.log = &log' \
    'transpiler\.linker\.log = &log' \
    'transpiler\.resolver\.log = old_log' \
    'transpiler\.linker\.log = old_log' \
    'jsc_vm\.log = old_log'; do
    if ! echo "$FUNC_BODY_NOCOMMENT" | grep -q "$pattern"; then
        echo "  MISSING: $pattern"
        P2P_OK=false
    fi
done

if [ "$P2P_OK" = true ]; then
    echo "PASS (0.10): Original resolver/linker log save/restore intact"
    PASS=$((PASS + 10))
else
    echo "FAIL (0.10): Original resolver/linker log save/restore broken"
fi

# [pr_diff] (0.05): _resolve call still present in the function
if echo "$FUNC_BODY_NOCOMMENT" | grep -q '_resolve('; then
    echo "PASS (0.05): _resolve call still present"
    PASS=$((PASS + 5))
else
    echo "FAIL (0.05): _resolve call missing — function gutted"
fi

##############################################################################
# Config-derived: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): No inline @import in functions — src/CLAUDE.md:11
if echo "$FUNC_BODY_NOCOMMENT" | grep -q '@import('; then
    echo "FAIL (0.05): Inline @import added to resolveMaybeNeedsTrailingSlash"
else
    echo "PASS (0.05): No inline @import in function"
    PASS=$((PASS + 5))
fi

# [agent_config] (0.05): No std.* API usage — src/CLAUDE.md:16
DIFF_CONTENT=$(git diff HEAD -- "$TARGET" 2>/dev/null || true)
if echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | grep -q 'std\.\(fs\|posix\|mem\|process\)'; then
    echo "FAIL (0.05): std.* API used instead of bun.*"
else
    echo "PASS (0.05): No std.* API usage in changes"
    PASS=$((PASS + 5))
fi

##############################################################################
# Ordering check (0.05): pm.log set BEFORE _resolve is called
##############################################################################
# [pr_diff] (0.05): The fix must set pm.log before the resolve call, not after
python3 -c "
import sys
body = '''$(echo "$BEFORE_DEFER" | sed "s/'/\\\\'/g")'''
lines = body.splitlines()
pm_log_line = -1
resolve_line = -1
for i, line in enumerate(lines):
    stripped = line.lstrip()
    if stripped.startswith('//'):
        continue
    if 'package_manager' in line and '.log' in line and '&log' in line:
        if pm_log_line == -1:
            pm_log_line = i
    if '_resolve(' in line:
        resolve_line = i
if pm_log_line >= 0 and resolve_line >= 0 and pm_log_line < resolve_line:
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "PASS (0.05): pm.log set before _resolve call"
    PASS=$((PASS + 5))
else
    echo "FAIL (0.05): pm.log not set before _resolve call (or ordering wrong)"
fi

##############################################################################
# Final score
##############################################################################

# Convert from integer centesimals to float
TOTAL=$(python3 -c "print(f'{$PASS / 100:.2f}')")

echo ""
echo "=== Final Score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# Compute component scores
python3 -c "
total = $PASS / 100
behavioral = min(0.55, ($PASS - min($PASS, 35)) / 100)  # rough
# Just output the total broken down
import json
result = {
    'reward': total,
    'behavioral': round(min(total, 0.60), 2),
    'regression': round(min(max(total - 0.60, 0), 0.15), 2),
    'config': round(min(max(total - 0.75, 0), 0.10), 2),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(result, f)
" 2>/dev/null || echo "{\"reward\": $TOTAL}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
