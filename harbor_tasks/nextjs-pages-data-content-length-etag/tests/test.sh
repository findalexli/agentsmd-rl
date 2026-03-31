#!/usr/bin/env bash
# Verifier for nextjs-pages-data-content-length-etag
#
# Bug: Buffer.from() wrapping in RenderResult construction causes isDynamic to
# return true, skipping Content-Length and ETag headers for /_next/data/ JSON
# responses and ISR fallback HTML responses in the Pages Router.
#
# The fix: pass plain strings (not Buffers) to RenderResult so isDynamic is false.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

HANDLER="packages/next/src/server/route-modules/pages/pages-handler.ts"
SEND_PAYLOAD="packages/next/src/server/send-payload.ts"

cd /workspace/next.js

###############################################################################
# GATE: Handler file exists and is non-empty
###############################################################################
if [ ! -f "$HANDLER" ] || [ ! -s "$HANDLER" ]; then
    echo "GATE FAILED: $HANDLER missing or empty"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

SCORE=0

###############################################################################
# TEST 1 [pr_diff] (0.40): Behavioral fail-to-pass — isDynamic mechanism
#
# Recreates the RenderResult class and sendRenderResult flow, proving:
#   - string input → isDynamic false → Content-Length + ETag set
#   - Buffer input → isDynamic true  → no Content-Length, no ETag
# Then reads the actual render-result.ts to confirm isDynamic still uses
# typeof check (so the mechanism test is valid).
# Finally verifies no RenderResult constructor call in the handler wraps
# its first argument in Buffer.from().
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.40) Behavioral: isDynamic → sendRenderResult chain"

node -e "
const fs = require('fs');
const assert = require('assert');

// === Part A: Reproduce the isDynamic → Content-Length mechanism ===
class RenderResult {
  constructor(response) { this.response = response; }
  get isDynamic() { return typeof this.response !== 'string'; }
  toUnchunkedString() {
    if (typeof this.response !== 'string') throw new Error('dynamic');
    return this.response;
  }
}

function simulateSendRenderResult(result) {
  const headers = {};
  const payload = result.isDynamic ? null : result.toUnchunkedString();
  if (payload !== null) {
    headers['ETag'] = '\"W/abc123\"';
    headers['Content-Length'] = String(Buffer.byteLength(payload));
  }
  return headers;
}

const testJson = JSON.stringify({ page: '/index', pageData: { x: 1 } });

// FIXED path: string → static → headers present
const fixedHeaders = simulateSendRenderResult(new RenderResult(testJson));
assert(fixedHeaders['Content-Length'] !== undefined,
  'FIXED: Content-Length must be set for string input');
assert(fixedHeaders['ETag'] !== undefined,
  'FIXED: ETag must be set for string input');

// BUGGY path: Buffer → dynamic → headers missing
const buggyHeaders = simulateSendRenderResult(new RenderResult(Buffer.from(testJson)));
assert(buggyHeaders['Content-Length'] === undefined,
  'BUGGY: Content-Length must NOT be set for Buffer input');
assert(buggyHeaders['ETag'] === undefined,
  'BUGGY: ETag must NOT be set for Buffer input');

console.log('Part A PASS: mechanism verified (string=static, Buffer=dynamic)');

// === Part B: Confirm render-result.ts still uses typeof for isDynamic ===
try {
  const rrSource = fs.readFileSync('packages/next/src/server/render-result.ts', 'utf8');
  // Strip comments
  const stripped = rrSource.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  if (!stripped.includes('isDynamic') || !stripped.includes('typeof')) {
    // If isDynamic was changed, our mechanism test may not apply — but
    // the fix might still be valid (e.g. isDynamic now returns false for Buffer).
    // Don't hard-fail, just warn.
    console.log('Part B WARN: isDynamic implementation may have changed');
  } else {
    console.log('Part B PASS: isDynamic uses typeof check');
  }
} catch (e) {
  console.log('Part B SKIP: render-result.ts not readable');
}

// === Part C: Verify handler RenderResult calls don't wrap arg in Buffer.from ===
const handler = fs.readFileSync('$HANDLER', 'utf8');
// Strip single-line and multi-line comments to prevent gaming via comments
const code = handler.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

const rrPattern = /new\s+RenderResult\s*\(/g;
let match;
let totalCalls = 0;
let bufferWrapped = 0;

while ((match = rrPattern.exec(code)) !== null) {
  totalCalls++;
  const pos = match.index + match[0].length;
  const after = code.substring(pos, pos + 300).trimStart();
  if (/^Buffer\.from\s*\(/.test(after)) {
    bufferWrapped++;
  }
}

if (totalCalls === 0) {
  console.log('Part C FAIL: no RenderResult constructors found in handler');
  process.exit(1);
}

if (bufferWrapped > 0) {
  console.log('Part C FAIL: ' + bufferWrapped + '/' + totalCalls +
    ' RenderResult calls still wrap first arg in Buffer.from');
  process.exit(1);
}

console.log('Part C PASS: ' + totalCalls + ' RenderResult calls, none use Buffer.from');
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.40)")
    echo "  PASS"
else
    echo "  FAIL"
fi

###############################################################################
# TEST 2 [pr_diff] (0.25): Fail-to-pass — data response + ISR fallback paths
#
# Checks that the two specific code paths (isNextDataRequest and ISR fallback)
# no longer wrap values in Buffer.from when constructing RenderResult.
# Uses JS parsing on comment-stripped code (not sed/grep).
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.25) Data response + ISR fallback paths fixed"

node -e "
const fs = require('fs');
const handler = fs.readFileSync('$HANDLER', 'utf8');
// Strip comments to prevent gaming
const code = handler.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

let passed = 0;
const subtests = 2;

// --- Subtest A: Data response path ---
// The data response path handles isNextDataRequest and serializes pageData
if (!code.includes('isNextDataRequest')) {
  console.log('A FAIL: isNextDataRequest handling not found');
} else {
  // Find the region around isNextDataRequest
  const idx = code.indexOf('isNextDataRequest');
  const region = code.substring(Math.max(0, idx - 50), idx + 1500);

  // Look for new RenderResult( in this region
  const rrMatch = /new\s+RenderResult\s*\(\s*Buffer\.from/m.test(region);
  if (rrMatch) {
    console.log('A FAIL: data path RenderResult still wraps arg in Buffer.from');
  } else {
    console.log('A PASS: data path RenderResult does not use Buffer.from');
    passed++;
  }
}

// --- Subtest B: ISR fallback path ---
// The ISR fallback reconstructs cached HTML into a RenderResult
const isrIdx = code.indexOf('isIsrFallback');
if (isrIdx === -1) {
  // Agent may have renamed/restructured; check that no Buffer.from wraps
  // RenderResult anywhere in the file (already covered by T1, but this
  // is a targeted check for the fallback path)
  const globalBufferRR = /new\s+RenderResult\s*\(\s*Buffer\.from/m.test(code);
  if (globalBufferRR) {
    console.log('B FAIL: Buffer.from still wraps a RenderResult call');
  } else {
    console.log('B PASS: no Buffer.from + RenderResult found (ISR path may be restructured)');
    passed++;
  }
} else {
  const isrRegion = code.substring(Math.max(0, isrIdx - 50), isrIdx + 1500);
  const isrBufferRR = /new\s+RenderResult\s*\(\s*Buffer\.from/m.test(isrRegion);
  if (isrBufferRR) {
    console.log('B FAIL: ISR fallback RenderResult still wraps arg in Buffer.from');
  } else {
    console.log('B PASS: ISR fallback RenderResult does not use Buffer.from');
    passed++;
  }
}

if (passed < subtests) {
  console.log('PARTIAL: ' + passed + '/' + subtests);
  process.exit(1);
}

console.log('ALL PASS');
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    echo "  PASS"
else
    echo "  FAIL"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): Pass-to-pass — sendRenderResult Content-Length flow
#
# The fix depends on sendRenderResult using isDynamic to decide whether to
# set Content-Length and ETag. Verify this logic chain is intact.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.15) P2P: sendRenderResult Content-Length flow"

node -e "
const fs = require('fs');
let source;
try {
  source = fs.readFileSync('$SEND_PAYLOAD', 'utf8');
} catch {
  // File may have been moved; search common locations
  const { execSync } = require('child_process');
  const found = execSync(
    'find packages/next/src/server -name \"send-payload*\" -o -name \"send-render*\" 2>/dev/null'
  ).toString().trim();
  if (found) {
    source = fs.readFileSync(found.split('\\n')[0], 'utf8');
  } else {
    console.log('FAIL: send-payload not found');
    process.exit(1);
  }
}

// Strip comments
const code = source.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// The critical chain: isDynamic check → payload extraction → Content-Length set
const hasIsDynamic = code.includes('isDynamic');
const hasContentLength = code.includes('Content-Length');
const hasByteLength = code.includes('byteLength');
const hasETag = code.includes('ETag');

const missing = [];
if (!hasIsDynamic) missing.push('isDynamic');
if (!hasContentLength) missing.push('Content-Length');
if (!hasByteLength) missing.push('byteLength');
if (!hasETag) missing.push('ETag');

if (missing.length > 0) {
  console.log('FAIL: sendRenderResult missing: ' + missing.join(', '));
  process.exit(1);
}

console.log('PASS: isDynamic → Content-Length + ETag chain intact');
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  PASS"
else
    echo "  FAIL"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): Pass-to-pass — handler retains core code paths
#
# The handler must still handle data requests, JSON serialization, and
# response sending. Checks comment-stripped code for real logic, not comments.
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) P2P: Handler core code paths intact"

node -e "
const fs = require('fs');
const handler = fs.readFileSync('$HANDLER', 'utf8');
const code = handler.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

const required = [
  ['isNextDataRequest', 'data request handling'],
  ['JSON.stringify', 'JSON serialization'],
  ['sendRenderResult', 'response sending'],
  ['RenderResult', 'RenderResult construction'],
  ['generateEtags', 'ETag generation flag'],
];

const missing = [];
for (const [keyword, desc] of required) {
  if (!code.includes(keyword)) missing.push(desc);
}

if (missing.length > 0) {
  console.log('FAIL: handler missing: ' + missing.join(', '));
  process.exit(1);
}

console.log('PASS: all core code paths present');
process.exit(0);
" 2>&1
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  PASS"
else
    echo "  FAIL"
fi

###############################################################################
# TEST 5 [structural] (0.10): Anti-stub — handler has substantial content
#
# Checks both total lines and non-comment code lines to reject trivial stubs.
###############################################################################
echo ""
echo "TEST 5: [structural] (0.10) Anti-stub check"

LINE_COUNT=$(wc -l < "$HANDLER")
CODE_LINES=$(grep -cvE '^\s*(//|/\*|\*|\*/|$)' "$HANDLER" 2>/dev/null || echo "0")

if [ "$LINE_COUNT" -gt 200 ] && [ "$CODE_LINES" -gt 100 ]; then
    echo "  PASS: $LINE_COUNT total lines, $CODE_LINES code lines"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL: $LINE_COUNT total / $CODE_LINES code — likely a stub"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "============================================"
echo "TOTAL SCORE: $SCORE"
echo "============================================"

echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
