#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
FILE="$REPO/packages/opencode/src/plugin/index.ts"
TEST_FILE="$REPO/packages/opencode/test/plugin/auth-override.test.ts"
REWARD=0

log() { echo "  $1"; }
pass() { log "PASS: $1"; REWARD=$(python3 -c "print(round($REWARD + $2, 4))"); }
fail() { log "FAIL: $1"; }

mkdir -p /logs/verifier

echo "=== GATE: File exists and is substantial ==="
# [pr_diff] (0.00): Target file must exist with real content
if [ ! -f "$FILE" ] || [ "$(wc -c < "$FILE")" -lt 500 ]; then
    log "GATE FAIL: file missing or too small"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE PASS: file exists"

echo ""
echo "=== Anti-stub gate ==="
# [pr_diff] (0.00): InstanceState.make must have substantial non-comment code
# Rejects stubs and comment-injection exploits
if ! node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const stateIdx = src.indexOf('InstanceState.make');
  if (stateIdx === -1) { process.exit(1); }
  const body = src.slice(stateIdx, stateIdx + 4000);
  // Count non-empty, non-comment lines
  const codeLines = body.split('\n').filter(l => {
    const t = l.trim();
    return t && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
  });
  if (codeLines.length < 40) { process.exit(1); }
  // Must reference key identifiers as actual code, not just in comments
  const hasHooks = /^\s*(?!\/\/).*\bhooks\b/.test(body.split('\n').find(l => !l.trim().startsWith('//') && /hooks/.test(l)) || '');
  const hasPlugins = /^\s*(?!\/\/).*\bINTERNAL_PLUGINS\b/.test(body.split('\n').find(l => !l.trim().startsWith('//') && /INTERNAL_PLUGINS/.test(l)) || '');
  const hasInput = /^\s*(?!\/\/).*\binput\b/.test(body.split('\n').find(l => !l.trim().startsWith('//') && /\binput\b/.test(l)) || '');
  if (!hasHooks || !hasPlugins || !hasInput) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    log "GATE FAIL: InstanceState.make body is a stub or missing key logic"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward": 0, "behavioral": 0, "regression": 0, "config": 0, "style_rubric": 0}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE PASS: InstanceState.make body is substantial"

echo ""
echo "=== Fail-to-pass: Bug anti-pattern removal ==="

# [pr_diff] (0.20): Monolithic Effect.promise(async () => {...}) wrapper removed
# BUG: InstanceState.make wraps all logic in one Effect.promise(async () => { ... })
# Any correct fix removes this — doesn't matter what replaces it
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const stateIdx = src.indexOf('InstanceState.make');
  if (stateIdx === -1) { process.exit(1); }
  const afterState = src.slice(stateIdx, stateIdx + 4000);
  // The buggy pattern: yield* Effect.promise(async () => { as the first yield in the function
  // wrapping hundreds of lines of logic
  const bugPattern = /yield\*\s+Effect\.promise\(async\s*\(\)\s*=>\s*\{/;
  if (bugPattern.test(afterState)) {
    process.exit(1);  // Bug still present
  }
  process.exit(0);
" 2>/dev/null; then
    pass "Monolithic Effect.promise(async) wrapper removed from InstanceState" 0.20
else
    fail "Monolithic Effect.promise(async () => {...}) still wraps InstanceState logic"
fi

# [pr_diff] (0.15): Config async facade no longer used
# BUG: code calls await Config.get() (static async facade) inside Effect.promise
# Any fix stops using the Config module's static async methods in the InstanceState body
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const stateIdx = src.indexOf('InstanceState.make');
  if (stateIdx === -1) { process.exit(1); }
  const body = src.slice(stateIdx, stateIdx + 4000);
  // Bug indicators: Config.get() used as async facade (not config.get() on yielded service)
  // We check for the capital-C Config.get() or await Config.get() pattern
  if (/await\s+Config\.get\(\)/.test(body)) { process.exit(1); }
  // Also check: cfg = Config.get() without await (still the facade)
  if (/=\s*Config\.get\(\)/.test(body)) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    pass "Config.get() async facade removed from InstanceState" 0.15
else
    fail "Still using Config.get() async facade in InstanceState"
fi

# [pr_diff] (0.15): Raw .catch() error handling replaced with Effect error channel
# BUG: plugin(input).catch(...) and applyPlugin(...).catch(...) bypass Effect error system
# Any fix replaces these with Effect-native error handling (tryPromise, catchAll, catchTag, etc.)
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const stateIdx = src.indexOf('InstanceState.make');
  if (stateIdx === -1) { process.exit(1); }
  const body = src.slice(stateIdx, stateIdx + 4000);
  // Bug: plugin(input).catch( — promise .catch for internal plugin loading
  if (/plugin\(input\)\.catch\s*\(/.test(body)) { process.exit(1); }
  // Bug: applyPlugin(load, input, hooks).catch( — promise .catch for external plugins
  if (/applyPlugin\([^)]*\)\.catch\s*\(/.test(body)) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    pass "Plugin .catch() replaced with Effect error handling" 0.15
else
    fail "Still using .catch() for plugin loading errors"
fi

# [pr_diff] (0.10): Trigger function no longer batches hooks in single promise
# BUG: trigger wraps all hooks in one Effect.promise(async () => { for...await })
# Any fix: per-hook yield, Effect.forEach, or other non-batched approach
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  // Find trigger function — search broadly for the hook iteration in trigger context
  // The bug: yield* Effect.promise(async () => { for (const hook of state.hooks)...await fn(
  const bugPattern = /yield\*\s+Effect\.promise\(async\s*\(\)\s*=>\s*\{[\s\S]{0,500}?for\s*\(const\s+hook\s+of\s+state\.hooks\)[\s\S]{0,300}?await\s+fn\s*\(/;
  if (bugPattern.test(src)) {
    process.exit(1);  // Bug still present
  }
  // Verify there's still SOME hook iteration (not deleted entirely)
  if (!/for\s*\(const\s+hook\s+of\s+state\.hooks\)/.test(src) &&
      !/state\.hooks\.(forEach|map|flatMap)/.test(src) &&
      !/Effect\.forEach.*state\.hooks/.test(src)) {
    process.exit(1);  // Hook iteration removed entirely
  }
  process.exit(0);
" 2>/dev/null; then
    pass "Trigger no longer batches hooks in single Effect.promise" 0.10
else
    fail "Trigger still batches hooks in one Effect.promise or hook iteration missing"
fi

# [pr_diff] (0.10): Config.defaultLayer provided in layer composition
# BUG: defaultLayer only provides Bus.layer, so yielding Config.Service would fail at runtime
# Any fix must include Config.defaultLayer somewhere in the layer graph
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  // Config.defaultLayer must appear in non-comment code
  const lines = src.split('\n');
  const found = lines.some(l => {
    const trimmed = l.trim();
    return !trimmed.startsWith('//') && !trimmed.startsWith('*') && /Config\.defaultLayer/.test(trimmed);
  });
  if (!found) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    pass "Config.defaultLayer included in layer composition" 0.10
else
    fail "Config.defaultLayer not provided — Config.Service would fail at runtime"
fi

# [pr_diff] (0.05): Config hook notification no longer uses bare try/catch
# BUG: the loop notifying plugins of config uses try { await hook.config?.() } catch {}
# Any fix replaces this with Effect error handling (tryPromise+ignore, catchAll, etc.)
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  // Find the config hook notification section
  // Look for the loop that calls .config?.() on hooks
  const patterns = [
    /for\s*\(const\s+hook\s+of\s+hooks\)[\s\S]{0,400}?\.config\?\./,
    /\/\/.*[Nn]otify.*plugin.*config[\s\S]{0,600}?\.config\?\./
  ];
  let hookSection = null;
  for (const p of patterns) {
    const m = src.match(p);
    if (m) { hookSection = m[0]; break; }
  }
  if (!hookSection) {
    // Config hook section might be restructured — only fail if try/catch is clearly present
    process.exit(0);
  }
  // Bug: bare try { ... } catch in the hook notification loop
  if (/\btry\s*\{/.test(hookSection)) {
    process.exit(1);
  }
  process.exit(0);
" 2>/dev/null; then
    pass "Config hook notification uses Effect error handling, not try/catch" 0.05
else
    fail "Config hook notification still uses bare try/catch"
fi

echo ""
echo "=== Regression: Pass-to-pass checks ==="

# [pr_diff] (0.05): Dynamic server import still present
# The dynamic import("../server/server") must still exist (any form)
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  // Check for dynamic import of server module in non-comment code
  const lines = src.split('\n');
  const found = lines.some(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && /import\s*\(.*server/.test(t);
  });
  if (!found) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    pass "Dynamic server import preserved" 0.05
else
    fail "Dynamic server import missing"
fi

# [pr_diff] (0.05): Error publishing to bus still references Session.Event.Error
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const lines = src.split('\n');
  const found = lines.some(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && /\.publish\(Session\.Event\.Error/.test(t);
  });
  if (!found) { process.exit(1); }
  process.exit(0);
" 2>/dev/null; then
    pass "Session.Event.Error publishing preserved" 0.05
else
    fail "Session.Event.Error publishing missing"
fi

# [pr_diff] (0.05): Test file updated to reflect new Effect patterns
# The auth-override test was checking for try/catch pattern — must be updated
if [ -f "$TEST_FILE" ] && node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$TEST_FILE', 'utf8');
  // The buggy test checks for try { ... } catch — the fix must update this
  // Just verify the old try/catch regex pattern is gone from the test
  if (/try\\\s\*\\\{/.test(src) && /catch\\\s\*\\\(err\\\)/.test(src)) {
    // Test still has the old try/catch regex pattern
    process.exit(1);
  }
  process.exit(0);
" 2>/dev/null; then
    pass "Test file updated (old try/catch pattern assertion removed)" 0.05
else
    fail "auth-override.test.ts still checks for old try/catch pattern"
fi

echo ""
echo "=== Config-derived checks ==="

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13 @ bb8d2cd
# Allow existing 'as any' casts but reject introducing many new ones
if node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$FILE', 'utf8');
  const anyCount = (src.match(/\bas\s+any\b/g) || []).length;
  // Original has ~2 casts; allow up to 5 for flexibility
  if (anyCount <= 5) { process.exit(0); }
  process.exit(1);
" 2>/dev/null; then
    pass "Limited 'as any' usage (AGENTS.md style)" 0.05
else
    fail "Excessive 'as any' casts introduced"
fi

echo ""
echo "=== Score ==="
FINAL=$(python3 -c "print(round($REWARD, 4))")
log "Final reward: $FINAL"
echo "$FINAL" > /logs/verifier/reward.txt

# Compute component breakdown
BEHAVIORAL=$(python3 -c "print(round(min($REWARD, 0.75), 4))")
REGRESSION=$(python3 -c "print(round(min(max($REWARD - 0.75, 0), 0.15), 4))")
CONFIG=$(python3 -c "print(round(min(max($REWARD - 0.90, 0), 0.05), 4))")
echo "{\"reward\": $FINAL, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0}" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
