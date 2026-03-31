#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

REPO="/workspace/openclaw"
HANDLER="$REPO/extensions/synology-chat/src/webhook-handler.ts"
TEST_UTILS="$REPO/extensions/synology-chat/src/test-http-utils.ts"

mkdir -p /logs/verifier

# ========== GATE: Files exist and parse ==========
# [pr_diff] (0): Required files must exist and have valid syntax

GATE_PASS=1
for f in "$HANDLER" "$TEST_UTILS"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "1" ]; then
    for f in "$HANDLER" "$TEST_UTILS"; do
        node -e "
          const fs = require('fs');
          const src = fs.readFileSync('$f', 'utf8');
          let depth = 0;
          for (const ch of src) {
            if (ch === '{') depth++;
            if (ch === '}') depth--;
          }
          if (Math.abs(depth) > 2) process.exit(1);
        " 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "GATE FAIL: $f has severely unbalanced braces"
            GATE_PASS=0
        fi
    done
fi

if [ "$GATE_PASS" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    echo "GATE FAILED"
    exit 0
fi

# ========== F2P BEHAVIORAL: Core in-flight guard integration ==========

# [pr_diff] (0.30): Handler integrates pre-auth concurrency guard with try/finally release
# Checks the PATTERN: in-flight guard wraps the pre-auth pipeline, released before delivery.
# Accepts: any variable names, try/finally OR promise .finally(), using keyword, etc.
# Anti-stub: requires real code structure, not just string presence.
F2P_CORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');

// 1. Must import in-flight utilities from webhook-ingress
const webhookIngress = src.match(/from\s*['\"]openclaw\/plugin-sdk\/webhook-ingress['\"]/)
if (!webhookIngress) {
  console.error('No import from openclaw/plugin-sdk/webhook-ingress');
  process.exit(1);
}

// 2. Must have a guard/pipeline call in the handler that can reject (returns early on !ok)
//    Accept: beginWebhookRequestPipelineOrReject, guardWebhookRequest, etc.
//    Key pattern: call returns {ok, release} and handler returns early if !ok
const hasGuardPattern =
  // Pattern A: const x = begin/guard...({...}); if (!x.ok) return;
  /(?:const|let)\s+\w+\s*=\s*(?:begin|guard|acquire)\w*\([\s\S]{0,200}?\bif\s*\(\s*!\s*\w+\.ok\b/.test(src) ||
  // Pattern B: const {ok, release} = ...; if (!ok) return;
  /(?:const|let)\s*\{\s*ok\s*,\s*release\s*\}[\s\S]{0,200}?\bif\s*\(\s*!ok\b/.test(src);

if (!hasGuardPattern) {
  console.error('No guard-and-reject pattern found in handler');
  process.exit(1);
}

// 3. Must release after pre-auth, before delivery. Accept multiple patterns:
const hasRelease =
  // Pattern A: try { ...auth... } finally { ...release() }
  /try\s*\{[\s\S]*?(?:parseAndAuthorize|readBody|readRequest)[\s\S]*?\}\s*finally\s*\{[\s\S]*?\.?release\s*\(/.test(src) ||
  // Pattern B: .finally(() => lifecycle.release())
  /\.finally\s*\(\s*\(\)\s*=>\s*\w+\.release\s*\(/.test(src) ||
  // Pattern C: using keyword (TS disposable)
  /using\s+\w+\s*=/.test(src);

if (!hasRelease) {
  console.error('No release mechanism (try/finally, .finally(), or using) found');
  process.exit(1);
}

// 4. Anti-stub: the handler function must have meaningful code (>15 non-empty, non-comment lines
//    between the guard call and the end of the function)
const handlerBody = src.match(/return\s+async\s+function[\s\S]*$/);
if (handlerBody) {
  const lines = handlerBody[0].split('\\n')
    .filter(l => l.trim() && !l.trim().startsWith('//') && !l.trim().startsWith('*'));
  if (lines.length < 15) {
    console.error('Handler too short - possible stub (' + lines.length + ' lines)');
    process.exit(1);
  }
}

console.log('Core in-flight guard integration verified');
" 2>/dev/null
[ $? -eq 0 ] && F2P_CORE=1
add_result 0.30 "$F2P_CORE" "pr_diff" "Handler integrates pre-auth concurrency guard with release lifecycle"

# [pr_diff] (0.15): In-flight key uses account-level scoping (not fragile remoteAddress)
# Behavioral: extract key computation, strip TS types, execute with mock data.
# Accepts: named function, arrow function, or inline key expression.
F2P_KEY=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');

// Strategy 1: Find a dedicated key function, extract it, run it
const fnPatterns = [
  // function getXxxInFlightKey(account) { ... }
  /function\s+\w*[Ii]n[Ff]light[Kk]ey\w*\s*\((\w+)[^)]*\)[^{]*\{([^}]*)\}/s,
  // function getXxxKey(account) { ... }  (near in-flight context)
  /function\s+\w*[Ww]ebhook[Kk]ey\w*\s*\((\w+)[^)]*\)[^{]*\{([^}]*)\}/s,
  // const getKey = (account) => account.accountId
  /(?:const|let)\s+\w*[Ii]n[Ff]light[Kk]ey\w*\s*=\s*\((\w+)[^)]*\)\s*(?::\s*\w+\s*)?=>\s*\{?([^;]*)/,
];

let executed = false;
for (const pat of fnPatterns) {
  const m = src.match(pat);
  if (!m) continue;
  const paramName = m[1];
  let body = m[2].trim();
  // Strip TS type annotations: ': TypeName', '<Generic>'
  body = body.replace(/:\s*[A-Z]\w*(\[\])?/g, '').replace(/<[^>]+>/g, '');
  // If body is a simple return, wrap it
  if (!body.startsWith('return') && !body.includes('{')) {
    body = 'return ' + body;
  }
  try {
    const fn = new Function(paramName, body);
    const result = fn({ accountId: 'test-acct-42', id: 'test-acct-42' });
    if (typeof result === 'string' && result.includes('test-acct-42')) {
      console.log('Key function returns account-scoped key (executed)');
      executed = true;
      break;
    }
  } catch(e) { /* extraction failed, try next pattern */ }
}

if (!executed) {
  // Strategy 2: Check inline key expression
  // e.g., inFlightKey: account.accountId  or  inFlightKey: getKey(account)
  const inlineKey = /[Ii]n[Ff]light[Kk]ey\s*[:=]\s*[\w.]*account[Ii]d/.test(src) ||
                    /[Ii]n[Ff]light[Kk]ey\s*[:=]\s*\w+\(\s*account\s*\)/.test(src);
  if (!inlineKey) {
    // Strategy 3: Verify accountId is used somewhere in the in-flight setup
    // and remoteAddress is NOT the key
    const guardCall = src.match(/(?:begin|guard|acquire)\w*\(\s*\{[\s\S]*?\}\s*\)/);
    if (!guardCall || !guardCall[0].includes('accountId')) {
      console.error('In-flight key does not use accountId');
      process.exit(1);
    }
    // Ensure remoteAddress is not the sole key
    if (guardCall[0].includes('remoteAddress') && !guardCall[0].includes('accountId')) {
      console.error('In-flight key uses fragile remoteAddress');
      process.exit(1);
    }
  }
  console.log('In-flight key is account-scoped (static check)');
}
" 2>/dev/null
[ $? -eq 0 ] && F2P_KEY=1
add_result 0.15 "$F2P_KEY" "pr_diff" "In-flight key uses account-level scoping"

# [pr_diff] (0.10): Module-level limiter instance exists (not created per-request)
# A per-request limiter would defeat the purpose — must be shared across requests.
F2P_MOD=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');

// Find top-level (module scope) limiter creation
// Must be outside any function definition
const lines = src.split('\\n');
let depth = 0;
let found = false;
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  // Track brace depth (rough but sufficient for module-scope detection)
  for (const ch of line) {
    if (ch === '{') depth++;
    if (ch === '}') depth--;
  }
  // At depth 0 or 1 (module scope), check for limiter factory call
  if (depth <= 1 && /(?:const|let)\s+\w+\s*=\s*(?:create|new\s+)\w*[Ii]n[Ff]light\w*\(/.test(line)) {
    found = true;
    break;
  }
}

if (!found) {
  console.error('No module-level in-flight limiter instance');
  process.exit(1);
}
console.log('Module-level limiter instance verified');
" 2>/dev/null
[ $? -eq 0 ] && F2P_MOD=1
add_result 0.10 "$F2P_MOD" "pr_diff" "Module-level in-flight limiter instance (shared across requests)"

# ========== F2P BEHAVIORAL: Test helper updated ==========

# [pr_diff] (0.10): makeRes() supports writable statusCode that syncs with _status
# The guard writes res.statusCode = 429; the test checks res._status. These must be linked.
# Accepts: defineProperty, Proxy, getter/setter, direct property, Object.create, etc.
F2P_RES=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TEST_UTILS', 'utf8');

// statusCode must appear in the source in non-comment context
const codeLines = src.split('\\n').filter(l => !l.trim().startsWith('//') && !l.trim().startsWith('*'));
const codeStr = codeLines.join('\\n');

if (!/statusCode/.test(codeStr)) {
  console.error('No statusCode in test-http-utils (excluding comments)');
  process.exit(1);
}

// Must be a real property mechanism, not just a string mention
// Accept any of: defineProperty, get/set accessor, Proxy, Object.create with descriptor
const mechanisms = [
  /defineProperty[\s\S]{0,100}statusCode/,
  /statusCode[\s\S]{0,100}defineProperty/,
  /set\s+statusCode/,
  /set\s*\(\s*\w*\s*\)[\s\S]{0,50}_status/,
  /statusCode[\s\S]{0,30}get\s*[\(:]|get\s*[\(:][^)]*\)[\s\S]{0,30}statusCode/,
  /new\s+Proxy/,
  /Object\.create\s*\(/,
  /_status\s*=\s*\w+[\s\S]{0,30}statusCode|statusCode[\s\S]{0,30}_status\s*=/,
];
const hasMechanism = mechanisms.some(p => p.test(codeStr));
if (!hasMechanism) {
  console.error('statusCode not backed by a real property mechanism');
  process.exit(1);
}

console.log('makeRes statusCode support verified');
" 2>/dev/null
[ $? -eq 0 ] && F2P_RES=1
add_result 0.10 "$F2P_RES" "pr_diff" "makeRes() supports writable statusCode property"

# ========== P2P: Existing behavior preserved ==========

# [pr_diff] (0.10): Clear-for-test function also resets in-flight limiter state
# Without this, tests leak state between runs.
P2P_CLEAR=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');

// Find the clear/reset-for-test function (accept various naming)
const clearFn = src.match(
  /(?:export\s+)?function\s+\w*(?:[Cc]lear|[Rr]eset)\w*(?:[Ff]or[Tt]est|[Ss]tate)\w*\s*\([^)]*\)[^{]*\{([\s\S]*?)\n\}/
);
if (!clearFn) {
  console.error('No test cleanup function found');
  process.exit(1);
}

const body = clearFn[1];
// Must reference the in-flight limiter (any naming: inFlight, inflight, concurrency, guard)
if (!/[Ii]n[Ff]light|concurrency[Gg]uard|limiter.*clear|\.clear\(\)/.test(body)) {
  // Check if the body has at least 3 .clear() calls (original has 2 maps + new limiter)
  const clearCalls = (body.match(/\.clear\s*\(/g) || []).length;
  if (clearCalls < 3) {
    console.error('Cleanup function does not appear to clear in-flight state');
    process.exit(1);
  }
}

console.log('Clear function handles in-flight state');
" 2>/dev/null
[ $? -eq 0 ] && P2P_CLEAR=1
add_result 0.10 "$P2P_CLEAR" "pr_diff" "Test cleanup function clears in-flight limiter state"

# [pr_diff] (0.05): Handler still rejects non-POST requests (existing behavior not broken)
P2P_METHOD=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');

// The handler must still check for POST method before or after the guard
// Accept: req.method !== 'POST', req.method === 'POST', etc.
if (!/req\.method\b/.test(src) || !/POST/.test(src)) {
  console.error('Handler lost method check');
  process.exit(1);
}

// Anti-regression: respondJson with 405 must still exist
if (!/405/.test(src)) {
  console.error('Handler lost 405 response');
  process.exit(1);
}

console.log('Method check preserved');
" 2>/dev/null
[ $? -eq 0 ] && P2P_METHOD=1
add_result 0.05 "$P2P_METHOD" "pr_diff" "Handler still rejects non-POST with 405"

# ========== Config-derived checks ==========

# [agent_config] (0.05): Imports from openclaw/plugin-sdk/* — extensions/AGENTS.md:19-20
CONFIG_IMPORT=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');
// Must not import from core internals
if (/from\s*['\"](?:src\/plugin-sdk|plugin-sdk-internal)/.test(src)) {
  console.error('Direct import from core internals');
  process.exit(1);
}
// New webhook-ingress import must use plugin-sdk path
if (!/openclaw\/plugin-sdk\/webhook-ingress/.test(src)) {
  console.error('webhook-ingress not imported from plugin-sdk path');
  process.exit(1);
}
console.log('Import boundaries OK');
" 2>/dev/null
[ $? -eq 0 ] && CONFIG_IMPORT=1
add_result 0.05 "$CONFIG_IMPORT" "agent_config" "Imports use openclaw/plugin-sdk/* path — extensions/AGENTS.md:19-20"

# [agent_config] (0.05): No any type annotations — CLAUDE.md:165
CONFIG_TYPING=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$HANDLER', 'utf8');
// Count ': any' outside of comments (rough filter)
const codeLines = src.split('\\n').filter(l => !l.trim().startsWith('//') && !l.trim().startsWith('*'));
const code = codeLines.join('\\n');
const anyMatches = code.match(/:\s*any\b/g) || [];
if (anyMatches.length > 0) {
  console.error('Found ' + anyMatches.length + ' uses of : any');
  process.exit(1);
}
console.log('No any types');
" 2>/dev/null
[ $? -eq 0 ] && CONFIG_TYPING=1
add_result 0.05 "$CONFIG_TYPING" "agent_config" "No any type annotations — CLAUDE.md:165"

# ========== Summary ==========

echo ""
echo "=== Test Results ==="
printf "$DETAILS"
echo ""
echo "Score: $SCORE / $TOTAL"

REWARD=$(python3 -c "
total = float('$TOTAL')
score = float('$SCORE')
r = score / total if total > 0 else 0.0
print(f'{min(1.0, max(0.0, r)):.4f}')
")

echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
total = float('$TOTAL')
score = float('$SCORE')
r = score / total if total > 0 else 0.0
r = min(1.0, max(0.0, r))
json.dump({'reward': round(r, 4)}, open('/logs/verifier/reward.json', 'w'))
"

echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
