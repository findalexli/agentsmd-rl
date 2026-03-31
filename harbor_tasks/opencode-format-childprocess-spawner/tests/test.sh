#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
REPO="/workspace/opencode"
FORMAT_TS="$REPO/packages/opencode/src/format/index.ts"
FORMAT_TEST="$REPO/packages/opencode/test/format/format.test.ts"

log() { echo "$1"; }

add() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

# ── GATE: File exists and is not truncated ─────────────────────────
# [static] (0.00): format/index.ts must exist and not be a stub
log "=== GATE: File exists and has substance ==="
if [ ! -f "$FORMAT_TS" ]; then
    log "GATE FAILED: format/index.ts does not exist"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
LINE_COUNT=$(wc -l < "$FORMAT_TS" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -lt 80 ]; then
    log "GATE FAILED: format/index.ts has only $LINE_COUNT lines — likely stubbed"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed ($LINE_COUNT lines)"

# ══════════════════════════════════════════════════════════════════════
# F2P-1 (0.25): formatFile uses ChildProcessSpawner to spawn, not Process.spawn
#
# The core bug: formatFile calls Process.spawn (raw utility) instead of using
# the Effect-native ChildProcessSpawner service. We verify:
#   a) Process.spawn is NOT called in formatFile body
#   b) ChildProcessSpawner IS yielded/used in the layer setup AND used to spawn in formatFile
#   c) These are in actual code, not comments
# [pr_diff] (0.25): formatFile must use ChildProcessSpawner instead of Process.spawn
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== F2P-1: ChildProcessSpawner replaces Process.spawn ==="
add_total 0.25
F2P1=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');

// Strip all comments (single-line and multi-line) to prevent comment injection gaming
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// a) Process.spawn must NOT be called anywhere in code
const hasProcessSpawn = /Process\.spawn\s*\(/.test(code);

// b) ChildProcessSpawner must be imported (from a real import statement)
const hasImport = /^import\s.*ChildProcessSpawner/m.test(code) ||
                  /^import\s.*from\s+['\"].*child.*process.*spawner/im.test(code) ||
                  /^import\s.*from\s+['\"]effect\/unstable\/process/m.test(code);

// c) ChildProcessSpawner must be yielded in the layer body (not just imported)
const hasYield = /yield\s*\*\s*ChildProcessSpawner/.test(code);

// d) spawner.spawn or .spawn( must be called in formatFile area
// Find formatFile function
const formatFileMatch = code.match(/function\s+formatFile[\s\S]*?(?=\n\s{8,}(?:log\.info\(['\"]init|function\s|const\s+\w+\s*=\s*Effect))/);
const hasSpawnerCall = formatFileMatch
  ? /(?:spawner|spawn)\s*[\.\(]/.test(formatFileMatch[0]) || /\.spawn\s*\(/.test(formatFileMatch[0])
  : false;

if (!hasProcessSpawn && hasImport && hasYield && hasSpawnerCall) {
  console.log('pass');
} else {
  const reasons = [];
  if (hasProcessSpawn) reasons.push('Process.spawn still present');
  if (!hasImport) reasons.push('no ChildProcessSpawner import');
  if (!hasYield) reasons.push('ChildProcessSpawner not yielded');
  if (!hasSpawnerCall) reasons.push('no spawner.spawn call in formatFile');
  console.log('fail:' + reasons.join(', '));
}
" 2>/dev/null || echo "error")

if [ "${F2P1%%:*}" = "pass" ]; then
    log "PASS: ChildProcessSpawner properly replaces Process.spawn"
    add 0.25
else
    log "FAIL: $F2P1"
fi

# ══════════════════════════════════════════════════════════════════════
# F2P-2 (0.20): formatFile returns an Effect, not a Promise
#
# The bug: formatFile is async (returns Promise), forcing the caller to wrap
# it with Effect.promise(). After fix, formatFile must return an Effect.
# We check: not async, uses Effect.gen or Effect.fn, has meaningful body.
# [pr_diff] (0.20): formatFile must be an Effect-returning function
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== F2P-2: formatFile returns Effect, not Promise ==="
add_total 0.20
F2P2=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find the formatFile definition line
const defLine = code.match(/(?:async\s+)?function\s+formatFile\b.*?\{|(?:const|let)\s+formatFile\s*=\s*(?:Effect\.fn|Effect\.gen)/m);
if (!defLine) {
  console.log('fail:formatFile function not found');
  process.exit(0);
}

const isAsync = /async\s+function\s+formatFile/.test(defLine[0]);

// Extract formatFile body (find it and go until matching brace depth or next top-level declaration)
const defIdx = code.indexOf(defLine[0]);
const afterDef = code.slice(defIdx);

// Check body has Effect usage (Effect.gen, Effect.fn, yield*, pipe, etc.)
const bodySlice = afterDef.slice(0, 2000); // reasonable body size
const usesEffect = /Effect\.gen|Effect\.fn|yield\s*\*/.test(bodySlice);
const hasSubstance = bodySlice.split('\\n').filter(l => l.trim().length > 0).length > 10;

if (isAsync) {
  console.log('fail:formatFile is still async');
} else if (!usesEffect) {
  console.log('fail:formatFile body does not use Effect');
} else if (!hasSubstance) {
  console.log('fail:formatFile body is too short (stub)');
} else {
  console.log('pass');
}
" 2>/dev/null || echo "error")

if [ "${F2P2%%:*}" = "pass" ]; then
    log "PASS: formatFile returns Effect"
    add 0.20
else
    log "FAIL: $F2P2"
fi

# ══════════════════════════════════════════════════════════════════════
# F2P-3 (0.15): file method composes formatFile natively (no Effect.promise wrapper)
#
# The bug: the file method wraps formatFile with Effect.promise() because
# formatFile returned a Promise. After fix, it should yield* formatFile directly.
# [pr_diff] (0.15): file method must not use Effect.promise to wrap formatFile
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== F2P-3: file method composes formatFile natively ==="
add_total 0.15
F2P3=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find the file method/const that references formatFile
// Look for a block containing both 'file' definition and 'formatFile'
const fileMethodPattern = /(?:const|let)\s+file\s*=[\s\S]{0,500}formatFile/;
const match = code.match(fileMethodPattern);

if (!match) {
  console.log('fail:file method referencing formatFile not found');
  process.exit(0);
}

const block = match[0];
// Must NOT wrap in Effect.promise
if (/Effect\.promise\s*\(\s*\(\)\s*=>\s*formatFile/.test(block) ||
    /Effect\.promise\s*\(\s*\(\)\s*=>\s*\w+\.formatFile/.test(block)) {
  console.log('fail:file method still wraps formatFile in Effect.promise');
} else if (/formatFile/.test(block)) {
  // formatFile is referenced without Effect.promise wrapper — good
  console.log('pass');
} else {
  console.log('fail:unexpected structure');
}
" 2>/dev/null || echo "error")

if [ "${F2P3%%:*}" = "pass" ]; then
    log "PASS: file method composes formatFile natively"
    add 0.15
else
    log "FAIL: $F2P3"
fi

# ══════════════════════════════════════════════════════════════════════
# F2P-4 (0.10): defaultLayer provides the spawner layer
#
# The bug: defaultLayer only provides Config.defaultLayer, not the spawner.
# After fix, it must also provide CrossSpawnSpawner (or equivalent) layer.
# [pr_diff] (0.10): defaultLayer must include spawner layer dependency
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== F2P-4: defaultLayer provides spawner layer ==="
add_total 0.10
F2P4=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find defaultLayer definition — look for the assignment through the next top-level declaration
const match = code.match(/(?:export\s+)?(?:const|let)\s+defaultLayer\s*=[\s\S]*?(?=\n\s*(?:export\s+)?(?:const|let|function|class)\s|\n\s*\})/);
if (!match) {
  console.log('fail:defaultLayer not found');
  process.exit(0);
}

const block = match[0];
// Must reference a spawner layer (CrossSpawnSpawner, ChildProcessSpawner layer, etc.)
// Accept any reasonable spawner layer name
const hasSpawnerLayer = /[Ss]pawner/i.test(block) && /[Ll]ayer|\.provide|\.merge|Layer\.mergeAll/.test(block);

if (hasSpawnerLayer) {
  console.log('pass');
} else {
  console.log('fail:defaultLayer does not reference a spawner layer');
}
" 2>/dev/null || echo "error")

if [ "${F2P4%%:*}" = "pass" ]; then
    log "PASS: defaultLayer provides spawner layer"
    add 0.10
else
    log "FAIL: $F2P4"
fi

# ══════════════════════════════════════════════════════════════════════
# P2P-1 (0.10): Format namespace still exports key members
#
# The fix is a refactor — existing public API must be preserved.
# [pr_diff] (0.10): Service, layer, defaultLayer, runPromise must still exist
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== P2P-1: Format exports preserved ==="
add_total 0.10
MISSING=""
for EXPORT in "Service" "layer" "defaultLayer" "runPromise"; do
    # Check in actual code (not comments)
    if ! node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
if (!code.includes('$EXPORT')) process.exit(1);
" 2>/dev/null; then
        MISSING="$MISSING $EXPORT"
    fi
done
if [ -z "$MISSING" ]; then
    log "PASS: All expected exports present"
    add 0.10
else
    log "FAIL: Missing exports:$MISSING"
fi

# ══════════════════════════════════════════════════════════════════════
# P2P-2 (0.05): Process import is removed (not just unused)
#
# Verify the old import is actually gone, not just unused.
# [pr_diff] (0.05): No import from util/process
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== P2P-2: Process import removed ==="
add_total 0.05
P2P2=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Check for import statement from util/process
if (/^import\s.*from\s+['\"].*util\/process/m.test(code)) {
  console.log('fail');
} else {
  console.log('pass');
}
" 2>/dev/null || echo "error")

if [ "$P2P2" = "pass" ]; then
    log "PASS: Process import removed"
    add 0.05
else
    log "FAIL: util/process import still present"
fi

# ══════════════════════════════════════════════════════════════════════
# F2P-5 (0.05): format.test.ts updated with spawner layer
#
# The test file must be updated to provide the spawner layer.
# [pr_diff] (0.05): test file must reference spawner layer
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== F2P-5: format.test.ts updated ==="
add_total 0.05
if [ -f "$FORMAT_TEST" ]; then
    F2P5=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TEST', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Test file should reference CrossSpawnSpawner or spawner layer or defaultLayer
if (/[Ss]pawner|Format\.defaultLayer/.test(code)) {
  console.log('pass');
} else {
  console.log('fail');
}
" 2>/dev/null || echo "error")
    if [ "$F2P5" = "pass" ]; then
        log "PASS: format.test.ts references spawner layer"
        add 0.05
    else
        log "FAIL: format.test.ts does not reference spawner layer"
    fi
else
    log "FAIL: format.test.ts not found"
fi

# ══════════════════════════════════════════════════════════════════════
# CONFIG-1 (0.05): no try/catch in formatFile
# [agent_config] (0.05): "Avoid try/catch where possible" — AGENTS.md:12 @ c8909908
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== CONFIG-1: no try/catch in formatFile ==="
add_total 0.05
CFG1=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$FORMAT_TS', 'utf8');
const code = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find formatFile body
const match = code.match(/function\s+formatFile[\s\S]*?(?=\n\s{6,}(?:log\.info\(['\"]init|function\s|const\s+\w+\s*=\s*Effect))/);
if (!match) {
  // formatFile might be defined differently (Effect.fn) — try broader match
  const altMatch = code.match(/formatFile[\s\S]{0,2000}/);
  if (altMatch && /\btry\s*\{/.test(altMatch[0])) {
    console.log('fail');
  } else {
    console.log('pass');
  }
} else if (/\btry\s*\{/.test(match[0])) {
  console.log('fail');
} else {
  console.log('pass');
}
" 2>/dev/null || echo "error")

if [ "$CFG1" = "pass" ]; then
    log "PASS: No try/catch in formatFile"
    add 0.05
else
    log "FAIL: formatFile still uses try/catch"
fi

# ══════════════════════════════════════════════════════════════════════
# CONFIG-2 (0.05): no `any` type introduced in changes
# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13 @ c8909908
# ══════════════════════════════════════════════════════════════════════
log ""
log "=== CONFIG-2: no any type in changes ==="
add_total 0.05
DIFF=$(cd "$REPO" && git diff HEAD -- packages/opencode/src/format/index.ts 2>/dev/null || echo "")
if echo "$DIFF" | grep -q '^\+.*:\s*any\b'; then
    log "FAIL: Added any type annotation in format/index.ts changes"
else
    log "PASS: No any types introduced"
    add 0.05
fi

# ── Final score ──────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
log "Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
