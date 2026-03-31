#!/usr/bin/env bash
set +e

SCORE=0
BEHAVIORAL_PASSED=0
REPO="/workspace/bun"
CLIENT="$REPO/test/bake/client-fixture.mjs"
HARNESS="$REPO/test/bake/bake-harness.ts"

##############################################################################
# GATE: Syntax check — file must parse as valid JavaScript
##############################################################################
# [pr_diff] (GATE): client-fixture.mjs must be valid JS
if ! node --check "$CLIENT" 2>/dev/null; then
  echo "GATE FAIL: client-fixture.mjs has syntax errors"
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0, "config": 0.0}' > /logs/verifier/reward.json
  echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi
echo "GATE PASS: client-fixture.mjs parses OK"

##############################################################################
# Helper: Extract loadPage() and run it against a controlled HTTP server.
#
# Anti-gaming: the test server tracks request count, and window.document.write
# tracks calls+content. A stub that never fetches gets requests=0 and
# writes=0, which we detect and reject. Any correct fix — regardless of
# implementation style — will fetch from the server and write to the document.
##############################################################################
cat > /tmp/extract_and_test.mjs << 'EXTRACTOR'
import http from 'node:http';
import fs from 'node:fs';

const CLIENT_PATH = process.argv[2];
const TEST_MODE = process.argv[3]; // 'null-ct', 'retry', 'valid'

const src = fs.readFileSync(CLIENT_PATH, 'utf8');

// Extract loadPage function using brace-depth matching
const startMatch = src.match(/async function loadPage\s*\([^)]*\)\s*\{/);
if (!startMatch) {
  console.log('NO_FUNC:requests=0:writes=0');
  process.exit(0);
}
const startIdx = startMatch.index;
let depth = 0;
let endIdx = startIdx;
for (let i = startIdx; i < src.length; i++) {
  if (src[i] === '{') depth++;
  if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
}
const funcSrc = src.substring(startIdx, endIdx);

// Track server requests and document.write calls
let requestCount = 0;
let writeCount = 0;
let writeContent = '';

const server = http.createServer((req, res) => {
  requestCount++;

  if (TEST_MODE === 'null-ct') {
    // Return 200 with NO content-type header → triggers null .match() bug
    res.writeHead(200);
    res.end('<html><head></head><body><script>1</script></body></html>');
  } else if (TEST_MODE === 'retry') {
    if (requestCount <= 2) {
      // Destroy connection to simulate transient failures
      req.socket.destroy();
      return;
    }
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end('<html><head></head><body><script>1</script></body></html>');
  } else if (TEST_MODE === 'valid') {
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end('<html><head></head><body><script>1</script></body></html>');
  }
});

server.listen(0, '127.0.0.1', async () => {
  const port = server.address().port;

  // Set up globals that loadPage() references, with instrumented document.write
  globalThis.url = `http://127.0.0.1:${port}`;
  globalThis.window = {
    document: {
      write: (content) => {
        writeCount++;
        writeContent += (content || '');
      }
    }
  };
  globalThis.exitCodeMap = { reloadFailed: 34 };

  // Intercept process.exit so the test stays alive
  let exitCode = null;
  const origExit = process.exit;
  process.exit = (code) => { exitCode = code; throw new Error('__EXIT__'); };

  // Safety timeout
  const timer = setTimeout(() => {
    process.exit = origExit;
    server.close();
    console.log(`TIMEOUT:requests=${requestCount}:writes=${writeCount}`);
    origExit(0);
  }, 15000);

  try {
    const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
    const testFn = new AsyncFunction(funcSrc + '\nawait loadPage();');
    await testFn();
    clearTimeout(timer);
    console.log(`OK:requests=${requestCount}:writes=${writeCount}`);
  } catch (e) {
    clearTimeout(timer);
    if (e.message === '__EXIT__') {
      console.log(`EXIT:${exitCode}:requests=${requestCount}:writes=${writeCount}`);
    } else if (e instanceof TypeError) {
      console.log(`TYPEERROR:${e.message}:requests=${requestCount}:writes=${writeCount}`);
    } else if (e.cause && (e.cause.code === 'ECONNRESET' || e.cause.code === 'ECONNREFUSED')) {
      console.log(`CONN_ERROR:requests=${requestCount}:writes=${writeCount}`);
    } else {
      console.log(`ERROR:${e.constructor.name}:${e.message}:requests=${requestCount}:writes=${writeCount}`);
    }
  } finally {
    process.exit = origExit;
    server.close();
  }
});
EXTRACTOR

##############################################################################
# F2P Test 1: Null content-type doesn't crash (0.30)
#
# The bug: loadPage() calls response.headers.get("content-type").match(...)
# without null check → TypeError when header is absent. Any fix that prevents
# the TypeError passes (optional chaining, null check, nullish coalescing, etc.)
#
# Anti-gaming: we verify requests>=1 (function actually fetched from server).
# A stub loadPage that never calls fetch() gets requests=0 and fails.
##############################################################################
# [pr_diff] (0.30): Null content-type header must not cause TypeError
RESULT=$(timeout 20 node /tmp/extract_and_test.mjs "$CLIENT" null-ct 2>/dev/null)
echo "  null-ct result: $RESULT"

# Parse request count from result
REQ_COUNT=$(echo "$RESULT" | grep -oP 'requests=\K[0-9]+' || echo "0")
STATUS=$(echo "$RESULT" | cut -d: -f1)

if { [ "$STATUS" = "OK" ] || [ "$STATUS" = "EXIT" ]; } && [ "$REQ_COUNT" -ge 1 ] 2>/dev/null; then
  SCORE=$((SCORE + 30))
  BEHAVIORAL_PASSED=1
  echo "PASS (0.30): Null content-type handled gracefully (requests=$REQ_COUNT)"
else
  echo "FAIL (0.30): Null content-type causes crash or no fetch occurred ($RESULT)"
fi

##############################################################################
# F2P Test 2: Retry on transient connection failures (0.25)
#
# The bug: fetch() with no retry → first connection error kills the process.
# Test server destroys the first 2 connections, then serves valid HTML.
# Any retry mechanism (for loop, while loop, recursive, etc.) that eventually
# succeeds will pass.
#
# Anti-gaming: we verify requests>=3 (function retried at least twice before
# succeeding). A stub or single-try function gets requests<=1 and fails.
##############################################################################
# [pr_diff] (0.25): loadPage() must retry fetch on transient connection errors
RESULT=$(timeout 20 node /tmp/extract_and_test.mjs "$CLIENT" retry 2>/dev/null)
echo "  retry result: $RESULT"

REQ_COUNT=$(echo "$RESULT" | grep -oP 'requests=\K[0-9]+' || echo "0")
WRITE_COUNT=$(echo "$RESULT" | grep -oP 'writes=\K[0-9]+' || echo "0")
STATUS=$(echo "$RESULT" | cut -d: -f1)

if [ "$STATUS" = "OK" ] && [ "$REQ_COUNT" -ge 3 ] 2>/dev/null; then
  # Function retried and eventually loaded the page successfully
  SCORE=$((SCORE + 25))
  BEHAVIORAL_PASSED=1
  echo "PASS (0.25): Retry logic works — survived transient failures (requests=$REQ_COUNT)"
elif { [ "$STATUS" = "EXIT" ] || [ "$STATUS" = "OK" ]; } && [ "$REQ_COUNT" -ge 2 ] 2>/dev/null; then
  # Retried but exhausted attempts and exited cleanly — partial credit
  SCORE=$((SCORE + 10))
  BEHAVIORAL_PASSED=1
  echo "PARTIAL (0.10/0.25): Retry attempted, but didn't fully recover (requests=$REQ_COUNT)"
else
  echo "FAIL (0.25): No retry — first connection failure crashes ($RESULT)"
fi

##############################################################################
# P2P Test: Valid HTML response still works (0.10)
#
# Regression check: a normal response with correct content-type and HTML
# must still load successfully after the fix. Verifies document.write is
# actually called (writes>=1), not just that it doesn't crash.
##############################################################################
# [repo_tests] (0.10): loadPage with valid response must still work
RESULT=$(timeout 20 node /tmp/extract_and_test.mjs "$CLIENT" valid 2>/dev/null)
echo "  valid result: $RESULT"

REQ_COUNT=$(echo "$RESULT" | grep -oP 'requests=\K[0-9]+' || echo "0")
WRITE_COUNT=$(echo "$RESULT" | grep -oP 'writes=\K[0-9]+' || echo "0")
STATUS=$(echo "$RESULT" | cut -d: -f1)

if [ "$STATUS" = "OK" ] && [ "$REQ_COUNT" -ge 1 ] && [ "$WRITE_COUNT" -ge 1 ] 2>/dev/null; then
  SCORE=$((SCORE + 10))
  echo "PASS (0.10): Valid HTML response handled correctly (requests=$REQ_COUNT, writes=$WRITE_COUNT)"
else
  echo "FAIL (0.10): Valid response broken or no fetch/write occurred ($RESULT)"
fi

##############################################################################
# Structural checks — GATED behind at least one behavioral test passing.
# If all behavioral tests fail, structural checks are skipped (anti-pattern #7 fix).
##############################################################################
if [ "$BEHAVIORAL_PASSED" -eq 0 ]; then
  echo ""
  echo "SKIP: All behavioral tests failed — structural checks gated"
else

  ##############################################################################
  # Structural: Initial page load wrapped in error handling (0.10)
  # WHY STRUCTURAL: The try/catch wraps the top-level `await loadPage()` call.
  # Testing it behaviorally would require making loadPage throw an unexpected
  # error that bypasses all internal handling — too fragile to engineer.
  ##############################################################################
  # [pr_diff] (0.10): Top-level loadPage() call must have error handling
  node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$CLIENT', 'utf8');
  // Find the section near 'Initial page load' or the last loadPage() invocation
  const lines = src.split('\n');
  let foundInitialSection = false;
  let hasTryCatch = false;
  let hasCatchMethod = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes('Initial page load') || line.includes('createWindow')) {
      foundInitialSection = true;
    }
    if (foundInitialSection) {
      if (line.startsWith('try') || line.includes('try {')) hasTryCatch = true;
      if (line.includes('.catch(') || line.includes('.catch (')) hasCatchMethod = true;
    }
  }
  // Anti-stub: if try/catch found, verify the catch block has meaningful content
  if (hasTryCatch) {
    const catchMatch = src.match(/\/\/\s*Initial page load[\s\S]*?catch\s*\([^)]*\)\s*\{([^}]*)\}/);
    if (catchMatch && catchMatch[1].trim().length < 5) {
      process.exit(1); // empty catch block = stub
    }
  }
  process.exit((hasTryCatch || hasCatchMethod) ? 0 : 1);
  " && {
    SCORE=$((SCORE + 10))
    echo "PASS (0.10): Initial page load has error handling"
  } || echo "FAIL (0.10): Initial page load missing error handling"

  ##############################################################################
  # Structural: unhandledRejection handler (0.10)
  # WHY STRUCTURAL: Process-level event handler requires the full client fixture
  # lifecycle with happy-dom + IPC; can't be triggered by extracting loadPage.
  ##############################################################################
  # [pr_diff] (0.10): Process must have unhandledRejection handler
  node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$CLIENT', 'utf8');
  const hasHandler = src.includes('unhandledRejection') &&
                     (src.includes('process.on') || src.includes('process.once') ||
                      src.includes('process.addListener'));
  // Anti-stub: handler callback must have a meaningful body (>10 non-whitespace chars)
  if (!hasHandler) process.exit(1);
  const handlerMatch = src.match(
    /process\.(on|once|addListener)\s*\(\s*['\"]unhandledRejection['\"]\s*,\s*(?:\([^)]*\)|[^,=]+)\s*=>\s*\{([\s\S]*?)\}/
  );
  if (!handlerMatch || handlerMatch[2].replace(/\\s/g, '').length < 10) process.exit(1);
  process.exit(0);
  " && {
    SCORE=$((SCORE + 10))
    echo "PASS (0.10): unhandledRejection handler present with body"
  } || echo "FAIL (0.10): No unhandledRejection handler (or stub)"

  ##############################################################################
  # Structural: Exit code propagated to OutputLineStream (0.10)
  # WHY STRUCTURAL: OutputLineStream is a Bun-internal class that requires
  # building Bun from source (C++/Zig) — infeasible in test container.
  ##############################################################################
  # [pr_diff] (0.10): Client exit code forwarded in bake-harness.ts
  node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$HARNESS', 'utf8');
  // Find the Client constructor and check for exit code handling
  // Accept any approach: proc.exited.then, proc.on('exit'), etc.
  const ctorMatch = src.match(/constructor\s*\([^)]*\)\s*\{[\s\S]*?(?=\n  \}|\n\t\})/);
  if (!ctorMatch) { process.exit(1); }
  const ctor = ctorMatch[0];
  const handlesExit = (
    (ctor.includes('exited') && ctor.includes('exitCode')) ||
    (ctor.includes('exit') && ctor.includes('output') && ctor.includes('exitCode')) ||
    (ctor.includes('proc.on') && ctor.includes('exit') && ctor.includes('exitCode'))
  );
  process.exit(handlesExit ? 0 : 1);
  " && {
    SCORE=$((SCORE + 10))
    echo "PASS (0.10): Exit code propagated in harness"
  } || echo "FAIL (0.10): Exit code not propagated"

fi  # end behavioral gate

##############################################################################
# Config: async/await pattern (0.05) — also gated behind behavioral
##############################################################################
if [ "$BEHAVIORAL_PASSED" -eq 1 ]; then
  # [agent_config] (0.05): "Prefer async/await over callbacks" — test/CLAUDE.md:104 @ 923690e
  node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$CLIENT', 'utf8');
  const startMatch = src.match(/async function loadPage/);
  if (!startMatch) process.exit(1);
  const startIdx = startMatch.index;
  let depth = 0, endIdx = startIdx;
  for (let i = startIdx; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
  }
  const fn = src.substring(startIdx, endIdx);
  const usesAwait = fn.includes('await');
  const avoidsThenChain = !fn.match(/fetch\([^)]*\)\.then/);
  process.exit((usesAwait && avoidsThenChain) ? 0 : 1);
  " && {
    SCORE=$((SCORE + 5))
    echo "PASS (0.05): Uses async/await per agent config"
  } || echo "FAIL (0.05): Does not follow async/await pattern"
fi

##############################################################################
# Final score
##############################################################################
FINAL=$(python3 -c "print(round($SCORE / 100, 4))")
echo ""
echo "Total score: $FINAL / 1.0"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE / 100
behavioral = min(score, 0.65)
rem = max(0, score - 0.65)
regression = min(rem, 0.10)
rem2 = max(0, rem - 0.10)
structural = min(rem2, 0.30)
config = max(0, rem2 - 0.30)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
    'config': round(config, 4)
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
