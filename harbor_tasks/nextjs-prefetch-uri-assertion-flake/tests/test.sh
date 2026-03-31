#!/usr/bin/env bash
set +e

TOTAL=0
TARGET="test/e2e/app-dir/app-prefetch/prefetching.test.ts"

pass() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE: File must exist and be substantial (original is ~430 lines) ──
if [ ! -s "$TARGET" ]; then
  echo "GATE FAIL: $TARGET missing or empty"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -lt 150 ]; then
  echo "GATE FAIL: $TARGET only $LINE_COUNT lines (expected ~430) — likely a stub"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: file exists ($LINE_COUNT lines)"

# ── F2P (0.35): Core fix — accordion-to-dashboard assertion must be inside retry() ──
# After clicking prefetch-via-link, the assertion on #accordion-to-dashboard must
# be wrapped in a retry/polling mechanism. The buggy code asserts immediately.
# Accepts: retry(), waitFor(), or any function wrapping the assertion.
# Uses brace-depth tracking instead of [^}]* to handle nested braces.
# [pr_diff] (0.35): Flaky accordion assertion must be retried after click
if python3 << 'PYEOF'
import re, sys

with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

# Find the target test body
m = re.search(r'should not unintentionally modify the requested prefetch', content)
if not m:
    print("  target test not found")
    sys.exit(1)

rest = content[m.end():]

# Find the click on prefetch-via-link (the actual .click() call, not the sanity check)
# Look for .click() near prefetch-via-link
click_match = re.search(r'prefetch-via-link[^)]*\)\.click\(\)', rest)
if not click_match:
    # Also accept elementById('prefetch-via-link') followed by .click()
    click_match = re.search(r'prefetch-via-link.*?\.click\(\)', rest, re.DOTALL)
if not click_match:
    print("  click on prefetch-via-link not found")
    sys.exit(1)

after_click = rest[click_match.end():]

# Find accordion-to-dashboard in the region after the click
acc_match = re.search(r'accordion-to-dashboard', after_click)
if not acc_match:
    print("  accordion-to-dashboard assertion not found after click")
    sys.exit(1)

# Check: is there a retry (or waitFor) call BEFORE the accordion assertion?
# Look in the text between click and accordion for retry( or waitFor(
region_before_acc = after_click[:acc_match.start()]

# Must find retry( or waitFor( that opens before the accordion assertion
if re.search(r'\bretry\s*\(', region_before_acc):
    # Verify the retry call is still open (brace-depth > 0) at the accordion position
    # Find the retry call position
    retry_m = re.search(r'\bretry\s*\(', region_before_acc)
    check_region = after_click[retry_m.start():acc_match.end() + 50]
    # Count braces/parens from retry to accordion — if depth > 0, accordion is inside
    depth = 0
    for ch in after_click[retry_m.start():acc_match.start()]:
        if ch in '({':
            depth += 1
        elif ch in ')}':
            depth -= 1
    if depth > 0:
        sys.exit(0)
    else:
        print("  retry found but accordion-to-dashboard is not inside it (depth=0)")

print("  no retry/waitFor wrapping accordion-to-dashboard after click")
sys.exit(1)
PYEOF
then
  pass 0.35 "accordion-to-dashboard assertion wrapped in retry() after click"
else
  fail 0.35 "accordion-to-dashboard assertion NOT retried after click"
fi

# ── F2P (0.10): Accordion assertion uses a valid element-check API ──
# Accept: hasElementByCss, waitForElementByCss, elementByCss, waitForSelector
# Reject: none specifically — the key fix is the retry wrapping, not the API name
# But verify SOME element-check method is used (not just a string literal)
# [pr_diff] (0.10): Accordion assertion uses a real element-check API
if python3 << 'PYEOF'
import re, sys

with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

m = re.search(r'should not unintentionally modify the requested prefetch', content)
if not m:
    sys.exit(1)
rest = content[m.end():]

# Find accordion-to-dashboard usage with a valid API method
# Accept any of: hasElementByCss, hasElementByCssSelector, waitForElementByCss,
# elementByCss, elementById, waitForSelector, querySelector
valid = re.search(
    r'(hasElementByCss|waitForElementByCss|elementByCss|elementById|'
    r'waitForSelector|querySelector)\s*\([^)]*accordion-to-dashboard',
    rest
)
if valid:
    sys.exit(0)

# Also accept: expect(...).toContain('accordion') or similar assertion patterns
if re.search(r'accordion-to-dashboard.*\b(toBe|toEqual|toBeTruthy|toBeDefined)\b', rest, re.DOTALL):
    sys.exit(0)

sys.exit(1)
PYEOF
then
  pass 0.10 "accordion assertion uses a valid element-check API"
else
  fail 0.10 "accordion assertion missing valid element-check method"
fi

# ── P2P (0.10): Other tests remain intact ──
# [pr_diff] (0.10): Other test cases not removed or renamed
if python3 << 'PYEOF'
import sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

required = [
    'should show layout eagerly when prefetched with loading one level down',
    'should not have prefetch error for static path',
    'should navigate when prefetch is false',
    'should not re-render error component when triggering a prefetch action',
    'should not fetch again when a static page was prefetched',
]
missing = [t for t in required if t not in content]
if missing:
    for t in missing:
        print(f"  Missing: {t}")
    sys.exit(1)
sys.exit(0)
PYEOF
then
  pass 0.10 "other tests remain intact"
else
  fail 0.10 "other tests missing or removed"
fi

# ── P2P (0.05): URI encoding assertions preserved ──
# The test's primary purpose is verifying URI encoding — these assertions must survive
# [pr_diff] (0.05): URI encoding test logic preserved
if python3 << 'PYEOF'
import sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

# The test must still check for the space-encoding behavior
if 'param=with%20space' in content and 'rscRequests' in content:
    sys.exit(0)
sys.exit(1)
PYEOF
then
  pass 0.05 "URI encoding assertions preserved"
else
  fail 0.05 "URI encoding test logic removed"
fi

# ── P2P (0.05): retry imported from next-test-utils ──
# [pr_diff] (0.05): retry import present
if python3 << 'PYEOF'
import re, sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()
# Accept any import bringing in retry from next-test-utils
if re.search(r'import\s*\{[^}]*\bretry\b[^}]*\}\s*from\s*[\'"]next-test-utils[\'"]', content):
    sys.exit(0)
sys.exit(1)
PYEOF
then
  pass 0.05 "retry imported from next-test-utils"
else
  fail 0.05 "retry not imported from next-test-utils"
fi

# ── Anti-stub (0.10): Target test body must be substantial ──
# The original test body has ~45 meaningful lines (setup, assertions, navigation)
# [pr_diff] (0.10): Target test body not hollowed out
if python3 << 'PYEOF'
import re, sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

m = re.search(r'should not unintentionally modify the requested prefetch', content)
if not m:
    sys.exit(1)

rest = content[m.end():]

# Find the approximate end of this test (next top-level it/describe or closing })
# Count meaningful lines in the first 60 lines
lines = rest.split('\n')[:60]
meaningful = 0
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith('//') and not stripped.startswith('*'):
        meaningful += 1

# Original has ~35+ meaningful lines; require at least 15
if meaningful >= 15:
    sys.exit(0)
print(f"  only {meaningful} meaningful lines (need >=15)")
sys.exit(1)
PYEOF
then
  pass 0.10 "target test body is substantial"
else
  fail 0.10 "target test body appears stubbed"
fi

# ── Config (0.10): Use retry() not setTimeout per CLAUDE.md ──
# [agent_config] (0.10): "Use retry() from next-test-utils instead of setTimeout" — CLAUDE.md:180 @ 138092696c
if python3 << 'PYEOF'
import re, sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

m = re.search(r'should not unintentionally modify the requested prefetch', content)
if not m:
    sys.exit(1)
rest = content[m.end():]

# Find click on prefetch-via-link
click_match = re.search(r'prefetch-via-link.*?\.click\(\)', rest, re.DOTALL)
if not click_match:
    sys.exit(1)

# Look in the FULL region after the click (not truncated at waitForIdleNetwork)
# for the retry wrapping and absence of setTimeout
after_click = rest[click_match.end():]
# Limit to ~80 lines (rest of this test)
lines = after_click.split('\n')[:80]
section = '\n'.join(lines)

has_retry = bool(re.search(r'\bretry\s*\(', section))
has_settimeout = 'setTimeout' in section

if has_retry and not has_settimeout:
    sys.exit(0)
sys.exit(1)
PYEOF
then
  pass 0.10 "uses retry() not setTimeout per CLAUDE.md"
else
  fail 0.10 "uses setTimeout or missing retry() after click"
fi

# ── Config (0.05): No deprecated check() per CLAUDE.md ──
# [agent_config] (0.05): "Do NOT use check() — it is deprecated" — CLAUDE.md:194 @ 138092696c
if python3 << 'PYEOF'
import re, sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

m = re.search(r'should not unintentionally modify the requested prefetch', content)
if not m:
    sys.exit(1)
rest = content[m.end():]

# Check ~80 lines for the test body
lines = rest.split('\n')[:80]
section = '\n'.join(lines)

if re.search(r'(?<!\w)check\s*\(', section):
    sys.exit(1)
sys.exit(0)
PYEOF
then
  pass 0.05 "no deprecated check() per CLAUDE.md"
else
  fail 0.05 "uses deprecated check()"
fi

# ── Anti-stub (0.05): accordion-to-dashboard string present ──
# [pr_diff] (0.05): Core assertion target present
if grep -q "accordion-to-dashboard" "$TARGET" 2>/dev/null; then
  pass 0.05 "accordion-to-dashboard assertion present"
else
  fail 0.05 "accordion-to-dashboard assertion removed"
fi

# ── Anti-stub (0.05): Navigation flow preserved — click + waitForIdleNetwork ──
# [pr_diff] (0.05): The test still performs the navigation + idle wait pattern
if python3 << 'PYEOF'
import sys
with open("test/e2e/app-dir/app-prefetch/prefetching.test.ts") as f:
    content = f.read()

# The target test must have the click and the subsequent idle network wait
if 'prefetch-via-link' in content and 'waitForIdleNetwork' in content:
    sys.exit(0)
sys.exit(1)
PYEOF
then
  pass 0.05 "navigation flow preserved (click + waitForIdleNetwork)"
else
  fail 0.05 "navigation flow missing"
fi

# ── Final score ──
echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
t = $TOTAL
beh = min(0.55, t)
reg = max(0, min(0.15, t - 0.55))
cfg = max(0, min(0.15, t - 0.70))
print('{\"reward\":' + str(t) + ',\"behavioral\":' + str(beh) + ',\"regression\":' + str(reg) + ',\"config\":' + str(cfg) + ',\"style_rubric\":0.0}')
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
