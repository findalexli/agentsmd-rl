#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/opencode"
VCS_TS="$REPO/packages/opencode/src/project/vcs.ts"

log() { echo "$1"; }
add() { SCORE=$(python3 -c "print(round($SCORE + $1, 4))"); }

mkdir -p /logs/verifier

# ── GATE: File exists and is non-trivial ─────────────────────────────
# [pr_diff] (0.00): vcs.ts must exist with substantial implementation
log "=== GATE: vcs.ts exists and is non-trivial ==="
if [ ! -f "$VCS_TS" ]; then
    log "GATE FAILED: vcs.ts missing"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
LINE_COUNT=$(wc -l < "$VCS_TS")
if [ "$LINE_COUNT" -lt 40 ]; then
    log "GATE FAILED: vcs.ts too short (${LINE_COUNT} lines), likely deleted or stubbed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed (${LINE_COUNT} lines)"

# ── F2P-1: Bug patterns removed ──────────────────────────────────────
# [pr_diff] (0.20): Effect.promise and @/util/git must both be gone
log ""
log "=== F2P-1: Bug patterns removed ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');
  const noPromise = !src.includes('Effect.promise');
  const noUtilGit = !src.includes('@/util/git');
  console.log(noPromise && noUtilGit ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Effect.promise and @/util/git both removed"
    add 0.20
else
    log "FAIL: Still has Effect.promise or @/util/git"
fi

# ── F2P-2: Async patterns replaced with generators ───────────────────
# [pr_diff] (0.15): Must use Effect generators, not async/await for git calls
log ""
log "=== F2P-2: Async replaced with generators ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');
  // No async arrow functions (const x = async (...) => )
  const noAsyncArrow = !/const\s+\w+\s*=\s*async\s*\(/.test(src);
  // No async function declarations
  const noAsyncFunc = !/async\s+function\s/.test(src);
  // Must have generator functions (Effect pattern)
  const hasGenerator = /function\s*\*/.test(src);
  console.log(noAsyncArrow && noAsyncFunc && hasGenerator ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Uses generators, no async patterns"
    add 0.15
else
    log "FAIL: Has async patterns or missing generators"
fi

# ── F2P-3: Git helper is a complete, non-stub implementation ─────────
# [pr_diff] (0.30): Generator uses native spawning, checks exit code, extracts output
log ""
log "=== F2P-3: Git helper implementation complete ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');
  const lines = src.split('\n');

  // Extract generator function bodies via brace-counting
  let depth = 0, inGen = false, genCode = '', generators = [];
  for (const line of lines) {
    if (/function\s*\*/.test(line) && !inGen) {
      inGen = true; depth = 0; genCode = '';
    }
    if (inGen) {
      genCode += line + '\n';
      for (const ch of line) {
        if (ch === '{') depth++;
        if (ch === '}') depth--;
      }
      if (depth <= 0 && genCode.length > 30) {
        generators.push(genCode);
        inGen = false;
      }
    }
  }

  // At least one generator must have ALL of these properties:
  // 1. yield* (awaiting Effect results)
  // 2. References native process spawning (ChildProcess, Spawner, Command, spawn, make)
  // 3. Checks process exit/return code
  // 4. Extracts text/stdout output
  // 5. Has >= 5 meaningful (non-empty, non-comment, non-brace-only) lines
  let found = false;
  for (const gen of generators) {
    const hasYield = /yield\s*\*/.test(gen);
    const hasProcessRef = /ChildProcess|Spawner|Command|spawn|\.make\s*\(/.test(gen);
    const checksExitCode = /\.code\b|\.exitCode\b|code\s*[!=]==?\s*0|exitCode\s*[!=]==?\s*0/.test(gen);
    const extractsOutput = /\.text\b|\.stdout\b|trim\s*\(/.test(gen);
    const meaningfulLines = gen.split('\n').filter(l =>
      l.trim() &&
      !l.trim().startsWith('//') &&
      !l.trim().startsWith('*') &&
      !/^\s*[{}]\s*$/.test(l)
    ).length;

    if (hasYield && hasProcessRef && checksExitCode && extractsOutput && meaningfulLines >= 5) {
      found = true;
      break;
    }
  }
  console.log(found ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Git helper has complete implementation"
    add 0.30
else
    log "FAIL: Git helper is missing, stubbed, or incomplete"
fi

# ── P2P-1: TypeScript compilation ─────────────────────────────────────
# [pr_diff] (0.10): Refactored vcs.ts must type-check without errors
log ""
log "=== P2P-1: TypeScript compilation ==="
cd "$REPO"
TSC_CHECKED=false
if timeout 180 npm install --ignore-scripts --no-audit --no-fund >/dev/null 2>&1; then
    log "npm install succeeded, running tsc..."
    TSC_OUT=$(timeout 120 npx tsc --noEmit -p packages/opencode/tsconfig.json 2>&1 || true)
    VCS_ERRORS=$(echo "$TSC_OUT" | grep "vcs\.ts" || true)
    TSC_CHECKED=true
    if [ -z "$VCS_ERRORS" ]; then
        log "PASS: vcs.ts has no TypeScript errors"
        add 0.10
    else
        log "FAIL: vcs.ts has TypeScript errors:"
        echo "$VCS_ERRORS" | head -5
    fi
else
    log "SKIP: npm install failed, cannot run tsc"
fi

# ── P2P-2: Public API exports intact ─────────────────────────────────
# [pr_diff] (0.10): Service public API must remain unchanged
log ""
log "=== P2P-2: Public API exports ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');
  const checks = [
    src.includes('export const layer'),
    src.includes('export const defaultLayer'),
    src.includes('export class Service'),
    /export\s+function\s+init/.test(src),
    /export\s+function\s+branch/.test(src),
  ];
  console.log(checks.every(Boolean) ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Public API intact"
    add 0.10
else
    log "FAIL: Missing public exports (layer, defaultLayer, Service, init, branch)"
fi

# ── STRUCT-1: Layer provides concrete spawner dependency ──────────────
# [pr_diff] (0.10): defaultLayer must wire in a concrete spawner implementation
log ""
log "=== STRUCT-1: Layer provides spawner ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');

  // Must import a concrete spawner implementation (accept various patterns)
  const importsSpawner = /import[\s\S]*?(?:CrossSpawn|cross-spawn|spawner)[\s\S]*?from/i.test(src);

  // defaultLayer must reference the spawner (Layer.provide, pipe, etc.)
  const dlIdx = src.indexOf('defaultLayer');
  const afterDL = dlIdx >= 0 ? src.substring(dlIdx, Math.min(dlIdx + 400, src.length)) : '';
  const dlRefersSpawner = /(?:Spawner|CrossSpawn|spawner)/i.test(afterDL);

  console.log(importsSpawner && dlRefersSpawner ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Layer provides spawner"
    add 0.10
else
    log "FAIL: Layer does not provide concrete spawner"
fi

# ── CONFIG-1: Effect.fn/fnUntraced for helpers ────────────────────────
# [agent_config] (0.05): "Effect.fn/fnUntraced for internal helpers" — packages/opencode/AGENTS.md
log ""
log "=== CONFIG-1: Effect function wrappers ==="
RESULT=$(node -e "
  const fs = require('fs');
  const src = fs.readFileSync('$VCS_TS', 'utf8');
  // Accept either Effect.fn or Effect.fnUntraced (both are valid patterns)
  const hasEffectFn = /Effect\.fn(?:Untraced)?\s*\(/.test(src);
  console.log(hasEffectFn ? 'pass' : 'fail');
" 2>/dev/null || echo "fail")
if [ "$RESULT" = "pass" ]; then
    log "PASS: Uses Effect.fn/fnUntraced"
    add 0.05
else
    log "FAIL: Not using Effect.fn/fnUntraced for helpers"
fi

# ── Final score ───────────────────────────────────────────────────────
log ""
log "=== FINAL ==="
FINAL=$(python3 -c "print(round($SCORE, 4))")
log "Score: $FINAL / 1.0"

echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
data = {
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.65), 4),
    'regression': round(min(max(score - 0.65, 0), 0.20), 4),
    'config': round(min(max(score - 0.85, 0), 0.05), 4),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
