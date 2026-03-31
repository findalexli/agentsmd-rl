#!/usr/bin/env bash
# Verifier for nextjs-urlhash-test-retry-flake
#
# Bug: url-hash.test.ts assertions fire before async browser state updates
# complete, causing intermittent flaky failures. Fix: wrap assertions in a
# retry/polling mechanism (e.g. retry(), toPass(), waitFor()).
#
# All checks are structural because Playwright e2e tests require a full
# Next.js dev server + browser that cannot run in the container.
# However, checks are designed as fail-to-pass where possible: they FAIL
# on the unmodified buggy code and PASS on any correct fix.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TEST_FILE="/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts"

###############################################################################
# GATE: Test file exists and has balanced braces
###############################################################################
if [ ! -f "$TEST_FILE" ]; then
    echo "GATE FAILED: $TEST_FILE missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
node -e "
const src = require('fs').readFileSync('$TEST_FILE', 'utf8');
let d = 0;
for (const c of src) { if (c==='{' || c==='(') d++; if (c==='}' || c===')') d--; if (d<0) process.exit(1); }
if (d !== 0) process.exit(1);
" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "GATE FAILED: $TEST_FILE has unbalanced syntax"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]      (0.25): F2P — flaky click-to-read chains removed
#   TEST 2 [pr_diff]      (0.30): F2P — assertions wrapped in retry/polling
#   TEST 3 [pr_diff]      (0.10): F2P — retry mechanism imported or defined
#   TEST 4 [pr_diff]      (0.10): P2P — describe blocks and test names preserved
#   TEST 5 [structural]   (0.10): Anti-stub — substantial content
#   TEST 6 [agent_config] (0.10): No deprecated check() — AGENTS.md:194 @ 78f73b2
#   TEST 7 [agent_config] (0.05): No setTimeout for waiting — AGENTS.md:180 @ 78f73b2
#   TOTAL                 = 1.00
###############################################################################

###############################################################################
# TEST 1 [pr_diff] (0.25): Fail-to-pass — flaky click→read chain patterns removed
#
# The buggy code chains .click() with .text() or .eval() in a single
# expression, reading browser state before async updates complete, e.g.:
#   const x = await browser.elementByCss('#a').click().elementByCss('p').text()
# ANY correct fix must break these chains. The buggy file has >=5 such chains.
# Also requires >=10 expect() calls remain (not just deleted).
###############################################################################
echo ""
echo "TEST 1: [pr_diff] Flaky click-to-read chain patterns removed"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

# Match .click() followed (with possible intermediate chains) by .text() or
# .eval() in the same expression. Use DOTALL to handle multiline chains.
# Pattern: .click() ... .text() or .click() ... .eval( on the same chain
chains = re.findall(
    r'\.click\(\)(?:\s*\.\w+\([^)]*\))*\s*\.(?:text|eval)\s*\(',
    src, re.DOTALL
)

# Must also still have meaningful assertions — prevent "just delete the tests"
expect_count = len(re.findall(r'\bexpect\s*\(', src))

if len(chains) >= 3:
    print(f"FAIL: {len(chains)} flaky click-to-read chains remain (expected <3)")
    sys.exit(1)

if expect_count < 10:
    print(f"FAIL: only {expect_count} expect() calls remain (expected >=10, tests may have been deleted)")
    sys.exit(1)

print(f"PASS: {len(chains)} click-to-read chains, {expect_count} expect() calls remain")
sys.exit(0)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [pr_diff] (0.30): Fail-to-pass — assertions wrapped in retry/polling
#
# The buggy code has 0 retry/polling wrappers around assertions. A correct
# fix wraps flaky assertions in retry(), toPass(), waitFor(), or similar.
# Accepts ANY retry/polling mechanism, not just retry() from next-test-utils.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] Assertions wrapped in retry/polling mechanism"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

# Count all standard retry/polling patterns — not just retry()
count = 0
for pattern in [
    r'\bretry\s*\(',                # retry() from next-test-utils or custom
    r'\.toPass\s*\(',               # Playwright expect().toPass()
    r'\bwaitFor\s*\(',              # Generic waitFor
    r'\bwaitForFunction\s*\(',      # Playwright page.waitForFunction
    r'\bpoll\s*\(',                 # Polling utility
]:
    count += len(re.findall(pattern, src))

if count >= 10:
    print(f"PASS: {count} retry/polling wrappers found (>= 10)")
    sys.exit(0)
elif count >= 5:
    print(f"PARTIAL PASS: {count} retry/polling wrappers found (>= 5, partial fix)")
    sys.exit(0)
else:
    print(f"FAIL: only {count} retry/polling wrappers found (expected >= 10)")
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [pr_diff] (0.10): Fail-to-pass — retry mechanism available
#
# The buggy code has no retry/polling utility. A correct fix must import or
# define one. Accepts: import { retry } from ANY module, const/function retry,
# toPass() usage, waitFor usage, or any custom retry function.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] Retry/polling mechanism imported or defined"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

checks = [
    re.search(r'import\s*\{[^}]*\bretry\b', src),           # import { retry } from ...
    re.search(r'import\s*\{[^}]*\bwaitFor\b', src),          # import { waitFor } from ...
    re.search(r'(?:const|let|var|function)\s+retry\b', src),  # locally defined retry
    re.search(r'\.toPass\s*\(', src),                         # Playwright toPass (no import needed)
    re.search(r'\bwaitForFunction\s*\(', src),                # Playwright waitForFunction
    re.search(r'require\s*\([^)]*\)\.retry\b', src),          # CJS require
]

if any(checks):
    print("PASS: retry/polling mechanism available")
    sys.exit(0)

print("FAIL: no retry/polling mechanism found")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [pr_diff] (0.10): Pass-to-pass — describe blocks and test names preserved
###############################################################################
echo ""
echo "TEST 4: [pr_diff] Existing describe blocks and test names preserved (P2P)"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

required = [
    "Client navigation with URL hash",
    "when hash changes",
    "should not run getInitialProps",
    "should scroll to the specified position",
    "should not scroll to hash when scroll={false}",
    "Should update asPath",
    "when hash changes with state",
    "should increment the history state counter",
    "should increment the shallow history state counter",
]

missing = [name for name in required if name not in src]
if missing:
    print(f"FAIL: missing test names/blocks: {missing}")
    sys.exit(1)

print("PASS: all expected describe/test blocks preserved")
sys.exit(0)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [structural] (0.10): Anti-stub — file has substantial content
###############################################################################
echo ""
echo "TEST 5: [structural] Anti-stub — substantial content"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    lines = f.readlines()
    src = ''.join(lines)

line_count = len(lines)
it_count = src.count("it(")
expect_count = src.count("expect(")

failures = []
if line_count < 150:
    failures.append(f"only {line_count} lines (expected >= 150)")
if it_count < 10:
    failures.append(f"only {it_count} it() blocks (expected >= 10)")
if expect_count < 10:
    failures.append(f"only {expect_count} expect() calls (expected >= 10)")

if failures:
    print(f"FAIL: {'; '.join(failures)}")
    sys.exit(1)

print(f"PASS: {line_count} lines, {it_count} it() blocks, {expect_count} expect() calls")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [agent_config] (0.10): No deprecated check() usage — AGENTS.md:194 @ 78f73b2
###############################################################################
echo ""
echo 'TEST 6: [agent_config] No deprecated check() usage — AGENTS.md:194 @ 78f73b2'
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

if re.search(r'\bawait\s+check\s*\(', src):
    print("FAIL: file uses deprecated check() — should use retry() + expect()")
    sys.exit(1)

print("PASS: no deprecated check() usage")
sys.exit(0)
PYEOF
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# TEST 7 [agent_config] (0.05): No setTimeout for waiting — AGENTS.md:180 @ 78f73b2
###############################################################################
echo ""
echo 'TEST 7: [agent_config] No setTimeout for waiting — AGENTS.md:180 @ 78f73b2'
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/pages-dir/client-navigation/url-hash.test.ts") as f:
    src = f.read()

if re.search(r'new\s+Promise.*setTimeout', src, re.DOTALL):
    print("FAIL: file uses setTimeout for waiting — should use retry()")
    sys.exit(1)

if re.search(r'await\s+new\s+Promise\s*\(\s*(?:resolve|r)\s*=>\s*setTimeout', src, re.DOTALL):
    print("FAIL: file uses setTimeout-based sleep — should use retry()")
    sys.exit(1)

print("PASS: no setTimeout waiting pattern")
sys.exit(0)
PYEOF
T7=$?
echo "  -> exit code: $T7"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.25 if $T1 == 0 else 0.0
t2 = 0.30 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.10 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (pr_diff: flaky chains removed)             = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 2 (pr_diff: assertions in retry/polling)      = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (pr_diff: retry mechanism available)         = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (pr_diff: test names preserved)              = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (structural: anti-stub)                      = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (agent_config: no deprecated check())        = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 7 (agent_config: no setTimeout waiting)        = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# Optional JSON output
python3 -c "
import json
data = {
    'reward': $SCORE,
    'behavioral': $(python3 -c "print(0.25 if $T1==0 else 0.0)") + $(python3 -c "print(0.30 if $T2==0 else 0.0)") + $(python3 -c "print(0.10 if $T3==0 else 0.0)") + $(python3 -c "print(0.10 if $T4==0 else 0.0)"),
    'structural': $(python3 -c "print(0.10 if $T5==0 else 0.0)"),
    'config': $(python3 -c "print(0.10 if $T6==0 else 0.0)") + $(python3 -c "print(0.05 if $T7==0 else 0.0)")
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
