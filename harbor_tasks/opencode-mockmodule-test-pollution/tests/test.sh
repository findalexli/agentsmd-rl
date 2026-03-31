#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/opencode"
THREAD_TEST="$REPO/packages/opencode/test/cli/tui/thread.test.ts"
CONFIG_TEST="$REPO/packages/opencode/test/config/config.test.ts"

log() { echo "$1"; }

mkdir -p /logs/verifier

# ── GATE: Files exist and aren't stubbed ──────────────────────────────
log "=== GATE: File existence and minimum size ==="
for f in "$THREAD_TEST" "$CONFIG_TEST"; do
    if [ ! -f "$f" ]; then
        log "GATE FAILED: $f does not exist"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
TL=$(wc -l < "$THREAD_TEST")
CL=$(wc -l < "$CONFIG_TEST")
if [ "$TL" -lt 30 ] || [ "$CL" -lt 150 ]; then
    log "GATE FAILED: files look stubbed (thread=$TL, config=$CL)"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed (thread=$TL lines, config=$CL lines)"

# ── F2P-1 (0.25): thread.test.ts runs successfully ──────────────────
# [pr_diff] (0.25): Modified thread tests must execute without errors
log ""
log "=== F2P-1: thread.test.ts runs successfully ==="
cd "$REPO"
THREAD_RESULT=$(timeout 120 bun test "$THREAD_TEST" 2>&1)
THREAD_EXIT=$?
if [ $THREAD_EXIT -eq 0 ]; then
    log "PASS: thread.test.ts passes"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    log "FAIL: thread.test.ts failed (exit=$THREAD_EXIT)"
    echo "$THREAD_RESULT" | tail -20
fi

# ── F2P-2 (0.20): config.test.ts runs successfully ──────────────────
# [pr_diff] (0.20): Config dependency install tests must work correctly
log ""
log "=== F2P-2: config.test.ts runs successfully ==="
cd "$REPO"
CONFIG_RESULT=$(timeout 180 bun test "$CONFIG_TEST" 2>&1)
CONFIG_EXIT=$?
if [ $CONFIG_EXIT -eq 0 ]; then
    log "PASS: config.test.ts passes"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    log "FAIL: config.test.ts failed (exit=$CONFIG_EXIT)"
    echo "$CONFIG_RESULT" | tail -20
fi

# ── F2P-3 (0.15): Mock leakage canary ───────────────────────────────
# [pr_diff] (0.15): Thread test mocks must not leak to subsequent test files
log ""
log "=== F2P-3: Mock state does not leak across test files ==="
# Create a canary test that runs AFTER thread.test.ts.
# If mock.module() leaked, the canary's require() returns the stub.
# With spyOn + mock.restore(), it returns the real module.
CANARY="$REPO/packages/opencode/test/cli/tui/zzz_canary_leak.test.ts"
cat > "$CANARY" << 'CANARYEOF'
import { describe, expect, test } from "bun:test"

describe("canary: mock leakage detection", () => {
  test("@/util/timeout module is not globally mocked", async () => {
    // thread.test.ts mocks @/util/timeout as { withTimeout: async (fn) => fn() }
    // If mock.module leaked, we get that stub. If spyOn was used, we get the real module.
    const mod = await import("../../../src/util/timeout")
    expect(mod).toBeDefined()

    // The real module's source file has actual implementation logic.
    // Check that the module has real exports (not a trivial stub).
    const keys = Object.keys(mod)
    expect(keys.length).toBeGreaterThan(0)

    // If withTimeout exists, verify it's not the trivial mock stub
    if (mod.withTimeout && typeof mod.withTimeout === "function") {
      // The mock stub is: async (fn) => fn()
      // Real implementation would have more complex source
      const src = mod.withTimeout.toString()
      expect(src.length).toBeGreaterThan(50)
    }
  })

  test("@/config/tui module is not globally mocked", async () => {
    const mod = await import("../../../src/config/tui")
    expect(mod).toBeDefined()

    // Real module should have meaningful exports beyond a simple stub
    const keys = Object.keys(mod)
    expect(keys.length).toBeGreaterThan(0)
  })
})
CANARYEOF

cd "$REPO"
# Run thread.test.ts first, then the canary catches any leaked mock state
CANARY_RESULT=$(timeout 120 bun test "$THREAD_TEST" "$CANARY" 2>&1)
CANARY_EXIT=$?
rm -f "$CANARY"

if [ $CANARY_EXIT -eq 0 ]; then
    log "PASS: No mock leakage detected"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    log "FAIL: Mock leakage or canary failure detected"
    echo "$CANARY_RESULT" | tail -20
fi

# ── F2P-4 (0.10): thread.test.ts does not use mock.module() ─────────
# [pr_diff] (0.10): mock.module() leaks globally in Bun; must be removed
log ""
log "=== F2P-4: No mock.module() in thread.test.ts ==="
NO_MOCK=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$THREAD_TEST', 'utf8');
  // Skip comments, count actual mock.module( calls
  const lines = src.split('\n');
  let inBlock = false;
  let found = 0;
  for (const line of lines) {
    const t = line.trim();
    if (t.startsWith('/*')) inBlock = true;
    if (inBlock) { if (t.includes('*/')) inBlock = false; continue; }
    if (t.startsWith('//')) continue;
    // Match mock.module( with optional whitespace
    if (/mock\s*\.\s*module\s*\(/.test(line)) found++;
  }
  console.log(found === 0 ? 'ok' : 'found_' + found);
" 2>/dev/null || echo "error")

if [ "$NO_MOCK" = "ok" ]; then
    log "PASS: No mock.module() calls"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: mock.module() still present ($NO_MOCK)"
fi

# ── F2P-5 (0.10): config.test.ts filters BunProc.run by cwd ────────
# [pr_diff] (0.10): Mock must only count calls for relevant directories
log ""
log "=== F2P-5: Config test filters BunProc.run mock by working directory ==="
CWD_FILTER=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$CONFIG_TEST', 'utf8');
  // Check that mockImplementation bodies reference opts.cwd or similar
  // to filter relevant calls from background noise
  const hasCwdAccess = /opts\??\s*\.\s*cwd|opts\s*&&\s*opts\s*\.\s*cwd/.test(src);
  // Must have some path comparison logic (normalize, ===, includes, startsWith)
  const hasComparison = /normalize|===.*dir|===.*cwd|startsWith|includes/.test(src);
  // The cwd access must be inside a mockImplementation context
  const inMockCtx = /mockImplementation[\s\S]{0,500}(opts\??\s*\.\s*cwd|opts\s*\.\s*cwd)/.test(src);
  console.log(hasCwdAccess && hasComparison && inMockCtx ? 'ok' : 'no_filter');
" 2>/dev/null || echo "error")

if [ "$CWD_FILTER" = "ok" ]; then
    log "PASS: BunProc.run mock filters by directory"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: BunProc.run mock does not filter by directory ($CWD_FILTER)"
fi

# ── P2P-1 (0.05): Test assertions and structure preserved ───────────
# [pr_diff] (0.05): Core test logic must not be gutted
log ""
log "=== P2P-1: Test structure preserved ==="
P2P_OK=$(node -e "
  const fs = require('fs');
  const t = fs.readFileSync('$THREAD_TEST', 'utf8');
  const c = fs.readFileSync('$CONFIG_TEST', 'utf8');
  // Thread test: must have describe, test/it, expect
  const tDescribe = (t.match(/describe\s*\(/g) || []).length >= 1;
  const tExpect = (t.match(/expect\s*\(/g) || []).length >= 2;
  const tTest = (t.match(/\btest\s*\(|\bit\s*\(/g) || []).length >= 1;
  // Config test: must have the dedupe/serialize test blocks
  const cDescribe = (c.match(/describe\s*\(/g) || []).length >= 1;
  const cExpect = (c.match(/expect\s*\(/g) || []).length >= 3;
  const ok = tDescribe && tExpect && tTest && cDescribe && cExpect;
  console.log(ok ? 'ok' : 'missing');
" 2>/dev/null || echo "error")

if [ "$P2P_OK" = "ok" ]; then
    log "PASS: Test structure preserved"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Test structure degraded ($P2P_OK)"
fi

# ── Anti-stub (0.05): Files are substantial ──────────────────────────
# [static] (0.05): Test files must not be stubbed out
log ""
log "=== STRUCTURAL: anti-stub ==="
if [ "$TL" -ge 40 ] && [ "$CL" -ge 200 ]; then
    log "PASS: thread.test.ts=$TL lines, config.test.ts=$CL lines"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Files look stubbed (thread=$TL, config=$CL)"
fi

# ── CONFIG-1 (0.05): Mock cleanup in lifecycle hook ──────────────────
# [agent_config] (0.05): "Avoid mocks as much as possible" — AGENTS.md:122 @ e973bbf5
log ""
log "=== CONFIG: Mock cleanup in lifecycle hook ==="
CLEANUP=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$THREAD_TEST', 'utf8');
  // Must have afterEach or afterAll calling mock.restore
  const hasAfterHook = /after(Each|All)\s*\(/.test(src);
  const hasRestore = /mock\s*\.\s*restore/.test(src);
  console.log(hasAfterHook && hasRestore ? 'ok' : 'missing');
" 2>/dev/null || echo "error")

if [ "$CLEANUP" = "ok" ]; then
    log "PASS: Mock cleanup in lifecycle hook"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: No mock cleanup in lifecycle hook ($CLEANUP)"
fi

# ── CONFIG-2 (0.05): No any type in changed code ────────────────────
# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13 @ e973bbf5
log ""
log "=== CONFIG: no any type in changes ==="
DIFF=$(cd "$REPO" && git diff HEAD -- \
    packages/opencode/test/cli/tui/thread.test.ts \
    packages/opencode/test/config/config.test.ts 2>/dev/null || echo "")
if echo "$DIFF" | grep -q '^\+.*:\s*any\b'; then
    log "FAIL: Added any type annotation"
else
    log "PASS: No any types added"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── Final score ──────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
log "Score: $SCORE / 1.00"

echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
# Approximate breakdown
behavioral = min(score, 0.60)
regression = min(max(score - 0.60, 0), 0.10)
config_score = min(max(score - 0.70, 0), 0.10)
json.dump({
    'reward': round(score, 2),
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config_score, 2)
}, open('/logs/verifier/reward.json', 'w'))
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
