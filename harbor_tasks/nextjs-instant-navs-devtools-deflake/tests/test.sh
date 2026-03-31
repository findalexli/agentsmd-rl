#!/usr/bin/env bash
# Verifier for nextjs-instant-navs-devtools-deflake
#
# Bug: clickStartClientNav uses elementByCssInstant which races Playwright IPC,
# causing sporadic timeouts in the instant-navs-devtools test.
#
# Fix: replace elementByCssInstant in clickStartClientNav with a selector method
# that accepts an explicit timeout, keeping other *instant usages intact.
#
# This is a Playwright e2e test requiring Next.js dev server + browser, so we
# cannot execute the test itself. All checks inspect the modified file, but are
# designed to accept ANY valid approach (not just the gold patch).
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TEST_FILE="/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts"

###############################################################################
# GATE: Test file exists and is non-trivial
###############################################################################
if [ ! -f "$TEST_FILE" ]; then
    echo "GATE FAILED: $TEST_FILE missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

LINE_COUNT=$(wc -l < "$TEST_FILE")
if [ "$LINE_COUNT" -lt 80 ]; then
    echo "GATE FAILED: file has only $LINE_COUNT lines — likely stubbed out"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED ($LINE_COUNT lines)"

###############################################################################
# Weight allocation:
#   TEST 1 [pr_diff]      (0.35): clickStartClientNav no longer races on elementByCssInstant
#   TEST 2 [pr_diff]      (0.25): Replacement uses an explicit timeout (reasonable value)
#   TEST 3 [pr_diff]      (0.10): Other instant-nav helpers still use fast/instant selectors
#   TEST 4 [pr_diff]      (0.10): waitForInstantModeCookie still called after click
#   TEST 5 [agent_config] (0.10): No deprecated check() usage — CLAUDE.md:194
#   TEST 6 [agent_config] (0.05): No Claude Code footers — CLAUDE.md:349
#   TEST 7 [structural]   (0.05): File retains describe block and multiple test cases
#   TOTAL                 = 1.00
###############################################################################

###############################################################################
# TEST 1 [pr_diff] (0.35): clickStartClientNav no longer races on elementByCssInstant
#
# Fail-to-pass: on the base commit, clickStartClientNav contains
# elementByCssInstant which causes the flake. ANY correct fix must remove this.
# Accepts: elementByCss, waitForSelector, locator, querySelector, or any other
# non-instant selector approach — we only check the *absence* of the racy call.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] clickStartClientNav does not use elementByCssInstant"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    src = f.read()

# Find the clickStartClientNav function body with flexible whitespace/indentation.
# Accept: async function, const arrow, or method syntax.
# Use a brace-depth counter to find the function body regardless of formatting.
patterns = [
    # async function clickStartClientNav(...)
    r'(?:async\s+)?function\s+clickStartClientNav\s*\([^)]*\)\s*\{',
    # const clickStartClientNav = async (...) => {
    r'(?:const|let|var)\s+clickStartClientNav\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*\w+\s*)?\s*=>\s*\{',
    # clickStartClientNav = async function(...)
    r'clickStartClientNav\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',
]

body = None
for pat in patterns:
    m = re.search(pat, src)
    if m:
        start = m.end() - 1  # position of opening brace
        depth = 0
        for i in range(start, len(src)):
            if src[i] == '{':
                depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0:
                    body = src[start+1:i]
                    break
        break

if body is None:
    # Function might have been renamed or restructured — check if the
    # data-instant-nav-client selector is handled somewhere without elementByCssInstant
    if '[data-instant-nav-client]' in src and 'elementByCssInstant' not in src:
        print("PASS: elementByCssInstant removed entirely from file (aggressive but valid fix)")
        sys.exit(0)
    if 'clickStartClientNav' not in src:
        print("FAIL: clickStartClientNav function not found and no alternative handler for [data-instant-nav-client]")
        sys.exit(1)
    print("FAIL: could not parse clickStartClientNav body")
    sys.exit(1)

if 'elementByCssInstant' in body:
    print("FAIL: clickStartClientNav still uses elementByCssInstant (the racy call)")
    sys.exit(1)

print("PASS: clickStartClientNav does not use elementByCssInstant")
sys.exit(0)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [pr_diff] (0.25): Replacement selector uses an explicit timeout
#
# The fix should add an explicit timeout to the selector call. We accept any
# method (elementByCss, waitForSelector, locator, etc.) as long as a timeout
# option is present with a reasonable value (1-5000ms). We also accept
# setTimeout/sleep-based waits as a lesser but valid approach.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] Replacement uses explicit timeout for [data-instant-nav-client] selector"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    src = f.read()

# Strategy: find the region that handles [data-instant-nav-client] and check
# that it has an explicit timeout. Accept many patterns.

# Find clickStartClientNav body (same flexible approach as T1)
patterns = [
    r'(?:async\s+)?function\s+clickStartClientNav\s*\([^)]*\)\s*\{',
    r'(?:const|let|var)\s+clickStartClientNav\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*\w+\s*)?\s*=>\s*\{',
    r'clickStartClientNav\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',
]

body = None
for pat in patterns:
    m = re.search(pat, src)
    if m:
        start = m.end() - 1
        depth = 0
        for i in range(start, len(src)):
            if src[i] == '{':
                depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0:
                    body = src[start+1:i]
                    break
        break

if body is None:
    # If function was inlined or renamed, look for timeout near the selector globally
    region = src
else:
    region = body

# Accept any of these patterns as providing a timeout:
# 1. elementByCss(..., { timeout: N }) or elementByCss(..., {timeout: N})
# 2. waitForSelector(..., { timeout: N })
# 3. locator(...).click({ timeout: N })
# 4. A timeout variable defined nearby
# 5. retry() or waitFor pattern with timeout
# 6. page.waitForSelector with timeout

timeout_patterns = [
    r'elementByCss\s*\([^)]*,\s*\{[^}]*timeout\s*:',
    r'waitForSelector\s*\([^)]*,?\s*\{[^}]*timeout\s*:',
    r'locator\s*\([^)]*\)[^;]*\.\s*click\s*\(\s*\{[^}]*timeout\s*:',
    r'timeout\s*[:=]\s*\d+',
    r'retry\s*\(',
    r'waitFor\s*\(',
    r'page\(\)\s*\.\s*waitForSelector\s*\([^)]*timeout',
]

for pat in timeout_patterns:
    if re.search(pat, region):
        # If we can extract the timeout value, validate it's reasonable
        val_match = re.search(r'timeout\s*[:=]\s*(\d+)', region)
        if val_match:
            val = int(val_match.group(1))
            if val > 30000:
                print(f"FAIL: timeout value {val}ms is unreasonably high (>30s) — defeats the purpose")
                sys.exit(1)
        print("PASS: selector replacement includes explicit timeout")
        sys.exit(0)

# Also accept if elementByCssInstant was replaced with a non-instant variant
# even without explicit timeout (the method itself may have a default timeout)
if 'elementByCss' in region and 'elementByCssInstant' not in region:
    print("PASS: uses elementByCss (which has default timeout, unlike *Instant variant)")
    sys.exit(0)

print("FAIL: no timeout mechanism found in clickStartClientNav")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [pr_diff] (0.10): Other instant-nav helpers still use fast selectors
#
# Pass-to-pass: getInstantNavPanelText and hasInstantNavPanelOpen should still
# work. We check that they exist (or equivalent functionality), but DON'T
# require them to use exactly elementByCssInstant — they could be refactored
# to use elementByCss with a short timeout and that's equally valid.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] Panel helper functions still exist and handle .instant-nav-panel"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    src = f.read()

# The test file should still have functions that read the instant-nav-panel.
# Accept either the original function names or the panel selector being used.
has_panel_text_fn = 'getInstantNavPanelText' in src
has_panel_open_fn = 'hasInstantNavPanelOpen' in src
has_panel_selector = '.instant-nav-panel' in src or 'instant-nav-panel' in src

if has_panel_text_fn or has_panel_open_fn:
    print("PASS: panel helper functions still present")
    sys.exit(0)

if has_panel_selector:
    print("PASS: instant-nav-panel selector still referenced (helpers may be inlined)")
    sys.exit(0)

print("FAIL: no panel helper functions or instant-nav-panel references found (regression)")
sys.exit(1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [pr_diff] (0.10): waitForInstantModeCookie still called after click
#
# The clickStartClientNav function must still wait for the instant mode cookie
# after performing the click. This is critical to test correctness — removing
# this wait would cause downstream test assertions to race.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] waitForInstantModeCookie still called in click flow"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    src = f.read()

# Check that waitForInstantModeCookie is still referenced
if 'waitForInstantModeCookie' not in src:
    print("FAIL: waitForInstantModeCookie removed from file entirely")
    sys.exit(1)

# Check it's still called in the click flow (either in clickStartClientNav
# or in the test bodies that call click + wait)
patterns = [
    r'(?:async\s+)?function\s+clickStartClientNav\s*\([^)]*\)\s*\{',
    r'(?:const|let|var)\s+clickStartClientNav\s*=\s*(?:async\s*)?\([^)]*\)\s*(?::\s*\w+\s*)?\s*=>\s*\{',
]

body = None
for pat in patterns:
    m = re.search(pat, src)
    if m:
        start = m.end() - 1
        depth = 0
        for i in range(start, len(src)):
            if src[i] == '{':
                depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0:
                    body = src[start+1:i]
                    break
        break

if body and 'waitForInstantModeCookie' in body:
    print("PASS: waitForInstantModeCookie called in clickStartClientNav")
    sys.exit(0)

# Also valid: the wait is done at the call site instead of inside the helper
if 'waitForInstantModeCookie' in src:
    print("PASS: waitForInstantModeCookie still used in test (may be at call site)")
    sys.exit(0)

print("FAIL: waitForInstantModeCookie not called after click")
sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [agent_config] (0.10): No deprecated check() usage — CLAUDE.md:194
# "Do NOT use check() — it is deprecated. Use retry() + expect() instead."
###############################################################################
echo ""
echo 'TEST 5: [agent_config] (0.10): No deprecated check() usage — CLAUDE.md:194 @ 60e71ac'
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    src = f.read()

# Match: await check( — but not inside single-line comments
# Split by lines to avoid matching inside comments
for i, line in enumerate(src.splitlines(), 1):
    stripped = line.lstrip()
    if stripped.startswith('//') or stripped.startswith('*'):
        continue
    if re.search(r'\bcheck\s*\(', stripped):
        # Make sure it's an await check() call, not something like checkbox.check()
        if re.search(r'await\s+check\s*\(', line) or re.search(r'^\s*check\s*\(', stripped):
            print(f"FAIL: deprecated check() usage at line {i}")
            sys.exit(1)

print("PASS: no deprecated check() usage")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [agent_config] (0.05): No Claude Code footers — CLAUDE.md:349
###############################################################################
echo ""
echo 'TEST 6: [agent_config] (0.05): No "Generated with Claude Code" footers — CLAUDE.md:349 @ 60e71ac'
node -e "
const {execSync} = require('child_process');
try {
    const log = execSync('git log --format=%B -n5 2>/dev/null || true', {encoding: 'utf8', cwd: '/workspace/next.js'});
    if (log.includes('Generated with Claude') || log.includes('Co-Authored-By: Claude')) {
        console.log('FAIL: commit message contains Claude footer');
        process.exit(1);
    }
} catch(e) {}
console.log('PASS');
"
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# TEST 7 [structural] (0.05): File retains describe block and multiple tests
###############################################################################
echo ""
echo "TEST 7: [structural] (0.05): File retains describe block and test cases"
python3 << 'PYEOF'
import sys

with open("/workspace/next.js/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts") as f:
    content = f.read()

if 'describe(' not in content:
    print("FAIL: no describe() block found")
    sys.exit(1)

# Count test cases — accept it( , test( , or it.each(
import re
test_count = len(re.findall(r'\b(?:it|test)\s*[\.(]', content))
if test_count < 3:
    print(f"FAIL: only {test_count} test cases (expected >= 3)")
    sys.exit(1)

print(f"PASS: {test_count} test cases in describe block")
sys.exit(0)
PYEOF
T7=$?
echo "  -> exit code: $T7"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
t7 = 0.05 if $T7 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6 + t7
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (pr_diff: no elementByCssInstant in clickStartClientNav)  = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (pr_diff: replacement has explicit timeout)               = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (pr_diff: panel helpers still present)                    = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (pr_diff: waitForInstantModeCookie still called)          = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (agent_config: no deprecated check())                     = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (agent_config: no Claude Code footers)                    = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 7 (structural: describe block + test cases)                 = $([ $T7 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
