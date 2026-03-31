#!/usr/bin/env bash
set +e

SCORE=0
TEST_FILE="test/e2e/app-dir/typed-routes/typed-routes.test.ts"

echo "=== Typed Routes Retry Timeout Flake ==="

# ── GATE: File exists and is non-trivial ─────────────────────────────
# [pr_diff] (0.00): Test file must exist and be substantial
echo "--- GATE: file exists ---"
if [ ! -f "$TEST_FILE" ]; then
  echo "GATE FAILED: $TEST_FILE does not exist"
  echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi
LINE_COUNT=$(wc -l < "$TEST_FILE")
if [ "$LINE_COUNT" -lt 40 ]; then
  echo "GATE FAILED: file too short ($LINE_COUNT lines) — likely stubbed"
  echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi
echo "  OK: $LINE_COUNT lines"

# ── GATE: Node can parse the TypeScript (basic syntax) ───────────────
# [pr_diff] (0.00): File must be parseable
echo "--- GATE: syntax ---"
if ! node -e "
const fs = require('fs');
const ts = fs.readFileSync('$TEST_FILE', 'utf8');
// Verify balanced braces/parens as basic syntax sanity
const pairs = [['{','}'],['(',')'],['[',']']];
for (const [o,c] of pairs) {
  const oc = (ts.match(new RegExp('\\\\' + o.replace(/[.*+?^${}()|[\]\\\\]/g,'\\\\$&'), 'g'))||[]).length;
  const cc = (ts.match(new RegExp('\\\\' + c.replace(/[.*+?^${}()|[\]\\\\]/g,'\\\\$&'), 'g'))||[]).length;
  if (Math.abs(oc - cc) > 3) { console.error('Unbalanced: '+o+'/'+c+' '+oc+'/'+cc); process.exit(1); }
}
console.log('Syntax OK');
" 2>&1; then
  echo "GATE FAILED: syntax"
  echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi

# ── F2P 1 (0.20): "should generate route types correctly" retry has extended timeout ──
# [pr_diff] (0.20): The retry() in this test must have a timeout >= 10s to prevent CI flakes
echo "--- F2P: generate route types retry timeout ---"
python3 -c "
import re, sys
with open('$TEST_FILE') as f:
    content = f.read()

# Find the test block for 'should generate route types correctly'
# Use a robust approach: find the it() call and extract its body
pattern = r\"it\(['\\\"]should generate route types correctly['\\\"].*?async\s*\(\)\s*=>\s*\{\"
m = re.search(pattern, content, re.DOTALL)
if not m:
    print('FAIL: test block not found')
    sys.exit(1)

# Extract from match to end of test block (find matching brace)
start = m.end()
depth = 1
i = start
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
block = content[m.start():i]

# Check for retry() call with a numeric timeout arg >= 10000
# Accept: retry(fn, 30000), retry(fn, 10000), retry(async () => {...}, 30_000)
timeout_match = re.search(r'retry\s*\([^)]*?}\s*,\s*(\d[\d_]*)\s*\)', block, re.DOTALL)
if not timeout_match:
    # Also accept timeout on its own line: }, 30000)
    timeout_match = re.search(r'}\s*,\s*(\d[\d_]*)\s*\)', block)
if timeout_match:
    val = int(timeout_match.group(1).replace('_', ''))
    if val >= 10000:
        print(f'PASS: timeout = {val}ms')
        sys.exit(0)
    else:
        print(f'FAIL: timeout = {val}ms (< 10000)')
        sys.exit(1)
else:
    print('FAIL: no extended timeout found on retry()')
    sys.exit(1)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.20)")
echo "  Score so far: $SCORE"

# ── F2P 2 (0.15): "should correctly convert custom route patterns" retry has extended timeout ──
# [pr_diff] (0.15): Same flake fix needed for custom route patterns test
echo "--- F2P: custom route patterns retry timeout ---"
python3 -c "
import re, sys
with open('$TEST_FILE') as f:
    content = f.read()

pattern = r\"it\(['\\\"]should correctly convert custom route patterns.*?async\s*\(\)\s*=>\s*\{\"
m = re.search(pattern, content, re.DOTALL)
if not m:
    print('FAIL: test block not found')
    sys.exit(1)

start = m.end()
depth = 1
i = start
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
block = content[m.start():i]

timeout_match = re.search(r'retry\s*\([^)]*?}\s*,\s*(\d[\d_]*)\s*\)', block, re.DOTALL)
if not timeout_match:
    timeout_match = re.search(r'}\s*,\s*(\d[\d_]*)\s*\)', block)
if timeout_match:
    val = int(timeout_match.group(1).replace('_', ''))
    if val >= 10000:
        print(f'PASS: timeout = {val}ms')
        sys.exit(0)
    else:
        print(f'FAIL: timeout = {val}ms (< 10000)')
        sys.exit(1)
else:
    print('FAIL: no extended timeout found on retry()')
    sys.exit(1)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.15)")
echo "  Score so far: $SCORE"

# ── F2P 3 (0.25): "should have passing tsc after start" waits for routes.d.ts BEFORE next.stop() ──
# [pr_diff] (0.25): The tsc test must read/wait for routes.d.ts before calling next.stop()
echo "--- F2P: tsc test waits for routes.d.ts before stop ---"
python3 -c "
import re, sys
with open('$TEST_FILE') as f:
    content = f.read()

pattern = r\"it\(['\\\"]should have passing tsc after start['\\\"].*?async\s*\(\)\s*=>\s*\{\"
m = re.search(pattern, content, re.DOTALL)
if not m:
    print('FAIL: tsc test block not found')
    sys.exit(1)

start = m.end()
depth = 1
i = start
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
block = content[m.start():i]

# The fix requires waiting for routes.d.ts to be generated before stopping the server.
# Accept any mechanism that reads/checks routes.d.ts before next.stop():
# - retry() with readFile + routes.d.ts
# - waitFor/waitUntil with routes.d.ts
# - any approach that references routes.d.ts before next.stop()

routes_pos = block.find('routes.d.ts')
stop_pos = block.find('next.stop()')

if routes_pos < 0:
    print('FAIL: no routes.d.ts reference in tsc test — server stopped without waiting for type generation')
    sys.exit(1)
if stop_pos < 0:
    print('FAIL: next.stop() not found in tsc test')
    sys.exit(1)
if routes_pos >= stop_pos:
    print('FAIL: routes.d.ts referenced AFTER next.stop() — must wait before stopping')
    sys.exit(1)

# Also verify the wait is in an async retry/wait pattern (not just a comment)
pre_stop = block[:stop_pos]
has_await_before = bool(re.search(r'await\s+.*routes\.d\.ts', pre_stop, re.DOTALL))
has_retry_before = bool(re.search(r'retry\s*\(', pre_stop))
has_wait_before = bool(re.search(r'(?:waitFor|waitUntil|readFile).*routes\.d\.ts', pre_stop, re.DOTALL))
if has_await_before or has_retry_before or has_wait_before:
    print('PASS: routes.d.ts awaited before next.stop()')
    sys.exit(0)
else:
    # Accept if routes.d.ts appears in any executable context (not just a comment)
    # Check it's not purely in a comment
    lines_before_stop = pre_stop.split('\\n')
    for line in lines_before_stop:
        stripped = line.strip()
        if 'routes.d.ts' in stripped and not stripped.startswith('//') and not stripped.startswith('*'):
            print('PASS: routes.d.ts referenced in code before next.stop()')
            sys.exit(0)
    print('FAIL: routes.d.ts only in comments before next.stop()')
    sys.exit(1)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.25)")
echo "  Score so far: $SCORE"

# ── F2P 4 (0.10): Retry in tsc test also has extended timeout ──
# [pr_diff] (0.10): The new retry in tsc test should also have extended timeout
echo "--- F2P: tsc test retry timeout ---"
python3 -c "
import re, sys
with open('$TEST_FILE') as f:
    content = f.read()

pattern = r\"it\(['\\\"]should have passing tsc after start['\\\"].*?async\s*\(\)\s*=>\s*\{\"
m = re.search(pattern, content, re.DOTALL)
if not m:
    print('FAIL: tsc test block not found')
    sys.exit(1)

start = m.end()
depth = 1
i = start
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
block = content[m.start():i]

# Find a retry call with timeout >= 10000 in this block
timeout_match = re.search(r'retry\s*\([^)]*?}\s*,\s*(\d[\d_]*)\s*\)', block, re.DOTALL)
if not timeout_match:
    timeout_match = re.search(r'}\s*,\s*(\d[\d_]*)\s*\)', block)
if timeout_match:
    val = int(timeout_match.group(1).replace('_', ''))
    if val >= 10000:
        print(f'PASS: timeout = {val}ms')
        sys.exit(0)
    else:
        print(f'FAIL: timeout = {val}ms (< 10000)')
        sys.exit(1)
else:
    # Accept other wait mechanisms (waitFor with timeout, etc.)
    if re.search(r'(waitFor|waitUntil)\s*\(.*\d{5,}', block, re.DOTALL):
        print('PASS: wait mechanism with extended timeout found')
        sys.exit(0)
    print('FAIL: no extended timeout found')
    sys.exit(1)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.10)")
echo "  Score so far: $SCORE"

# ── P2P (0.10): Original test assertions preserved ──────────────────
# [pr_diff] (0.10): Key assertions from the original tests must still be present
echo "--- P2P: original assertions preserved ---"
python3 -c "
import sys
with open('$TEST_FILE') as f:
    content = f.read()

# These are actual assertion strings from the original test file that must be preserved.
# They test the BEHAVIOR of route type generation, not just structure.
required = [
    'expectedDts',                          # The expected DTS content variable
    'toContain(expectedDts)',               # Core assertion: generated types match expected
    'routes.d.ts',                          # The generated file being tested
    'pnpm',                                 # tsc test uses pnpm
    'tsc',                                  # tsc test runs TypeScript compiler
    '/blog/[category]/[[...slug]]',         # Custom route pattern assertion
    '/api-legacy/[version]/[[...endpoint]]', # Custom route pattern assertion
]

missing = [r for r in required if r not in content]
if missing:
    print(f'FAIL: missing original assertions: {missing}')
    sys.exit(1)
else:
    print(f'PASS: all {len(required)} original assertions present')
    sys.exit(0)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.10)")
echo "  Score so far: $SCORE"

# ── P2P (0.05): All original test names present ─────────────────────
# [pr_diff] (0.05): All test blocks from the original file must still exist
echo "--- P2P: test names preserved ---"
P2P_OK=true
for TEST_NAME in \
  "should generate route types correctly" \
  "should have passing tsc after start" \
  "should correctly convert custom route patterns" \
  "should generate RouteContext type" \
; do
  if ! grep -q "$TEST_NAME" "$TEST_FILE"; then
    echo "  FAIL: missing test '$TEST_NAME'"
    P2P_OK=false
  fi
done
if $P2P_OK; then
  echo "  PASS: all original test names present"
  SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
echo "  Score so far: $SCORE"

# ── Config (0.05): Uses retry() not setTimeout ──────────────────────
# [agent_config] (0.05): "Use retry() from next-test-utils instead of setTimeout for waiting" — AGENTS.md:180 @ 0090db224d
echo "--- Config: retry not setTimeout ---"
if grep -q 'setTimeout' "$TEST_FILE" 2>/dev/null; then
  echo "  FAIL: found setTimeout usage"
else
  echo "  PASS: no setTimeout"
  SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
echo "  Score so far: $SCORE"

# ── Config (0.05): No deprecated check() ────────────────────────────
# [agent_config] (0.05): "Do NOT use check() - it is deprecated" — AGENTS.md:194 @ 0090db224d
echo "--- Config: no deprecated check() ---"
if grep -P '^\s*await\s+check\s*\(' "$TEST_FILE" 2>/dev/null; then
  echo "  FAIL: found deprecated check() call"
else
  echo "  PASS: no deprecated check()"
  SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
echo "  Score so far: $SCORE"

# ── Anti-stub (0.05): Retry blocks contain actual assertions ────────
# [pr_diff] (0.05): retry() calls must wrap real expect() assertions, not be empty
echo "--- Anti-stub: retry bodies have assertions ---"
python3 -c "
import re, sys
with open('$TEST_FILE') as f:
    content = f.read()

# Find all retry() blocks and check they contain expect() calls
retry_blocks = list(re.finditer(r'retry\s*\(\s*async\s*\(\)\s*=>\s*\{', content))
if len(retry_blocks) < 3:
    print(f'FAIL: only {len(retry_blocks)} retry blocks (need >= 3)')
    sys.exit(1)

empty_retries = 0
for m in retry_blocks:
    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    body = content[start:i-1]
    if 'expect(' not in body and 'assert' not in body.lower():
        empty_retries += 1

if empty_retries > 0:
    print(f'FAIL: {empty_retries} retry block(s) with no assertions')
    sys.exit(1)
else:
    print(f'PASS: all {len(retry_blocks)} retry blocks contain assertions')
    sys.exit(0)
" 2>&1 && SCORE=$(python3 -c "print($SCORE + 0.05)")
echo "  Score so far: $SCORE"

# ── Final score ──────────────────────────────────────────────────────
echo ""
echo "=== Final Score: $SCORE / 1.00 ==="
mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM judge
source /tests/judge_hook.sh 2>/dev/null || true
