#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
REPO="/workspace/opencode"
FILE="$REPO/packages/ui/src/components/message-part.tsx"

log() { echo "$1"; }

# ── GATE: File exists and has core SolidJS markers ───────────────────
# [pr_diff] (0.00): File must exist with PART_MAPPING and createSignal
log "=== GATE: File exists and is valid ==="
if [ ! -f "$FILE" ] || [ ! -s "$FILE" ]; then
    log "GATE FAILED: message-part.tsx missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');
  if (!src.includes('PART_MAPPING') || !src.includes('createSignal')) process.exit(1);
" 2>/dev/null; then
    log "GATE FAILED: message-part.tsx missing core SolidJS structure"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed"

# ── F2P-1: The 100ms throttle interval bug is fixed ─────────────────
# [pr_diff] (0.25): Render pacing interval must be reduced from ~100ms to ≤50ms
log ""
log "=== F2P-1: Throttle interval reduced from 100ms ==="
TOTAL=$(python3 -c "print($TOTAL + 0.25)")
F2P1_RESULT=$(node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');

  // Work in the utility section (before PART_MAPPING assignments)
  const utilSection = src.split(/PART_MAPPING\s*\[/)[0] || src;

  // Find all 'const NAME = NUMBER' in the utility area
  const constMatches = [...utilSection.matchAll(/const\s+(\w+)\s*=\s*(\d+)/g)];

  // Find setTimeout / requestAnimationFrame calls
  const timeoutMatches = [...utilSection.matchAll(/setTimeout\s*\([^,]+,\s*(\w+|\d+)/g)];
  const hasRAF = /requestAnimationFrame/.test(utilSection);

  // Check 1: the old >=80ms throttle constant must be gone
  let hasOldThrottle = false;
  for (const m of constMatches) {
    const val = parseInt(m[2]);
    if (val >= 80 && val <= 150) {
      const name = m[1];
      const usedInTimeout = timeoutMatches.some(t => t[1] === name);
      const looksLikeTiming = /throttle|interval|pace|tick|delay|render|ms|cadence/i.test(name);
      if (usedInTimeout || looksLikeTiming) hasOldThrottle = true;
    }
  }
  for (const m of timeoutMatches) {
    const val = parseInt(m[1]);
    if (!isNaN(val) && val >= 80 && val <= 150) hasOldThrottle = true;
  }

  // Check 2: a fast timing constant (<=50ms) or requestAnimationFrame must exist
  let hasFastInterval = hasRAF;  // RAF is ~16ms, counts as fast
  for (const m of constMatches) {
    const val = parseInt(m[2]);
    if (val > 0 && val <= 50) {
      const name = m[1];
      const usedInTimeout = timeoutMatches.some(t => t[1] === name);
      const looksLikeTiming = /throttle|interval|pace|tick|delay|render|ms|cadence/i.test(name);
      if (usedInTimeout || looksLikeTiming) hasFastInterval = true;
    }
  }
  for (const m of timeoutMatches) {
    const val = parseInt(m[1]);
    if (!isNaN(val) && val > 0 && val <= 50) hasFastInterval = true;
  }

  if (!hasOldThrottle && hasFastInterval) console.log('OK');
  else if (hasOldThrottle) console.log('STILL_SLOW');
  else console.log('NO_INTERVAL');
" 2>/dev/null || echo "ERROR")

if [ "$F2P1_RESULT" = "OK" ]; then
    log "PASS: Timing interval reduced to ≤50ms"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    log "FAIL: Old throttle still present or no fast interval: $F2P1_RESULT"
fi

# ── F2P-2: Pacing function is streaming-aware ────────────────────────
# [pr_diff] (0.20): Pacing must consider whether the stream is still active
log ""
log "=== F2P-2: Pacing function is streaming-aware ==="
TOTAL=$(python3 -c "print($TOTAL + 0.20)")
F2P2_RESULT=$(node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');
  const utilSection = src.split(/PART_MAPPING\s*\[/)[0] || src;

  // Find the main pacing/throttle factory: a function containing createSignal + setTimeout
  // Works for both 'function name(...)' and 'const name = (...) =>' patterns
  let pacingFunc = null;

  // Try function declarations
  const funcPattern = /function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\{/g;
  let m;
  while ((m = funcPattern.exec(utilSection)) !== null) {
    const start = m.index;
    let depth = 0, bodyStart = utilSection.indexOf('{', start + m[0].length - 1), bodyEnd = bodyStart;
    for (let i = bodyStart; i < utilSection.length; i++) {
      if (utilSection[i] === '{') depth++;
      if (utilSection[i] === '}') depth--;
      if (depth === 0) { bodyEnd = i; break; }
    }
    const body = utilSection.substring(bodyStart, bodyEnd + 1);
    if (body.includes('createSignal') && (body.includes('setTimeout') || body.includes('requestAnimationFrame'))) {
      pacingFunc = { name: m[1], params: m[2], body };
      break;
    }
  }

  // Try arrow function / const pattern
  if (!pacingFunc) {
    const arrowPattern = /(?:const|let)\s+(\w+)\s*=\s*\(([^)]*)\)\s*(?::\s*[^=>{]+)?\s*=>/g;
    while ((m = arrowPattern.exec(utilSection)) !== null) {
      const ctx = utilSection.substring(m.index, Math.min(m.index + 3000, utilSection.length));
      if (ctx.includes('createSignal') && (ctx.includes('setTimeout') || ctx.includes('requestAnimationFrame'))) {
        pacingFunc = { name: m[1], params: m[2], body: ctx };
        break;
      }
    }
  }

  if (!pacingFunc) { console.log('NO_FUNC'); process.exit(0); }

  // Check: does the function accept a streaming/live parameter? (buggy version has 1 param)
  const paramList = pacingFunc.params.split(',').map(p => p.trim()).filter(Boolean);
  const multipleParams = paramList.length >= 2;

  // Or does the body reference streaming/live state?
  const bodyRefsStreaming = /\b(streaming|live|isStreaming|isLive|active|isActive|running|flushed|complete)\b/i.test(pacingFunc.body);

  // Also check: do the call sites pass a streaming argument?
  const afterUtil = src.substring(src.indexOf('PART_MAPPING'));
  const callsWithMultipleArgs = new RegExp(pacingFunc.name + '\\s*\\([^)]+,\\s*[^)]+\\)').test(afterUtil);

  if (multipleParams || bodyRefsStreaming || callsWithMultipleArgs) console.log('OK');
  else console.log('NOT_AWARE:params=' + paramList.length);
" 2>/dev/null || echo "ERROR")

if [ "$F2P2_RESULT" = "OK" ]; then
    log "PASS: Pacing function is streaming-aware"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    log "FAIL: Pacing not streaming-aware: $F2P2_RESULT"
fi

# ── F2P-3: Incremental reveal logic (not whole-buffer dump) ──────────
# [pr_diff] (0.20): Text must be revealed in small increments, not dumped all at once
log ""
log "=== F2P-3: Incremental reveal logic exists ==="
TOTAL=$(python3 -c "print($TOTAL + 0.20)")
F2P3_RESULT=$(node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');
  const utilSection = src.split(/PART_MAPPING\s*\[/)[0] || src;

  // The buggy code does setValue(next) — dumps entire buffer at once.
  // A correct fix needs incremental position tracking. Look for signals of this:

  // 1. substring/slice to reveal partial text
  const hasSubstring = /\.substring\s*\(|\.slice\s*\(|\.substr\s*\(/.test(utilSection);

  // 2. A position/cursor variable that gets incremented
  const hasPositionTracking = /\b(pos|position|cursor|idx|start|offset|shown|revealed|current)\b\s*(\+\=|\=\s*\w+\s*\+)/.test(utilSection);

  // 3. Step/increment arithmetic (Math.min, Math.ceil, etc. combined with size/step/chunk logic)
  const hasMathCalc = /Math\.(min|ceil|floor|max)\s*\(/.test(utilSection);
  const hasStepLogic = /\b(step|increment|chunk|advance|stride)\b/i.test(utilSection);
  const hasStepCalc = hasMathCalc && hasStepLogic;

  // 4. A loop advancing through text positions
  const hasAdvanceLoop = /for\s*\(\s*let\s+\w+\s*=\s*\w+\s*;\s*\w+\s*</.test(utilSection);

  // Need at least 2 signals to confirm incremental reveal
  const signals = [hasSubstring, hasPositionTracking, hasStepCalc, hasAdvanceLoop].filter(Boolean).length;

  if (signals >= 2) console.log('OK');
  else if (signals === 1) console.log('WEAK');
  else console.log('NO_INCREMENTAL');
" 2>/dev/null || echo "ERROR")

if [ "$F2P3_RESULT" = "OK" ]; then
    log "PASS: Incremental reveal logic found"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
elif [ "$F2P3_RESULT" = "WEAK" ]; then
    log "PARTIAL: Weak evidence of incremental reveal (half credit)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: No incremental reveal logic: $F2P3_RESULT"
fi

# ── P2P-1: Both TextPartDisplay and ReasoningPartDisplay use pacing ──
# [pr_diff] (0.15): Both components must use the pacing mechanism
log ""
log "=== P2P-1: Both displays use the pacing mechanism ==="
TOTAL=$(python3 -c "print($TOTAL + 0.15)")
P2P1_RESULT=$(node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');
  const utilSection = src.split(/PART_MAPPING\s*\[/)[0] || src;

  // Find the pacing function name (the function with createSignal + setTimeout/RAF)
  let pacingName = null;
  const funcPattern = /function\s+(\w+)\s*\([^)]*\)/g;
  let m;
  while ((m = funcPattern.exec(utilSection)) !== null) {
    const ctx = utilSection.substring(m.index, Math.min(m.index + 3000, utilSection.length));
    if (ctx.includes('createSignal') && (ctx.includes('setTimeout') || ctx.includes('requestAnimationFrame'))) {
      pacingName = m[1]; break;
    }
  }
  if (!pacingName) {
    const arrowPattern = /(?:const|let)\s+(\w+)\s*=\s*\(/g;
    while ((m = arrowPattern.exec(utilSection)) !== null) {
      const ctx = utilSection.substring(m.index, Math.min(m.index + 3000, utilSection.length));
      if (ctx.includes('createSignal') && (ctx.includes('setTimeout') || ctx.includes('requestAnimationFrame'))) {
        pacingName = m[1]; break;
      }
    }
  }
  if (!pacingName) { console.log('NO_PACING_FUNC'); process.exit(0); }

  // Check both components reference the pacing function
  const afterUtil = src.substring(src.indexOf('PART_MAPPING'));
  const textBlock = afterUtil.match(/PART_MAPPING\s*\[\s*['\"]text['\"]\s*\][\s\S]*?(?=PART_MAPPING\s*\[|$)/);
  const reasonBlock = afterUtil.match(/PART_MAPPING\s*\[\s*['\"]reasoning['\"]\s*\][\s\S]*?(?=PART_MAPPING\s*\[|$)/);

  const textUses = textBlock && textBlock[0].includes(pacingName);
  const reasonUses = reasonBlock && reasonBlock[0].includes(pacingName);

  if (textUses && reasonUses) console.log('OK');
  else console.log('MISSING:text=' + !!textUses + ',reason=' + !!reasonUses);
" 2>/dev/null || echo "ERROR")

if [ "$P2P1_RESULT" = "OK" ]; then
    log "PASS: Both TextPartDisplay and ReasoningPartDisplay use pacing"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    log "FAIL: Not both components use pacing: $P2P1_RESULT"
fi

# ── F2P-4: Word boundary snapping in reveal positions ────────────────
# [pr_diff] (0.05): Reveal positions should snap to natural text breaks
log ""
log "=== F2P-4: Word boundary snapping ==="
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
SNAP_RESULT=$(node -e "
  const src = require('fs').readFileSync('$FILE', 'utf8');
  const utilSection = src.split(/PART_MAPPING\s*\[/)[0] || src;

  // Look for any regex that matches whitespace/punctuation (word boundary detection)
  // Name-agnostic: just find a regex literal containing \\s and punctuation chars
  const regexLiterals = [...utilSection.matchAll(/\/\[([^\]]+)\]\//g)];
  let hasBoundaryRegex = false;
  for (const m of regexLiterals) {
    const chars = m[1];
    // A boundary regex should match spaces and at least some punctuation
    if ((chars.includes('\\\\s') || chars.includes(' ')) &&
        (chars.includes('.') || chars.includes(',') || chars.includes('!'))) {
      hasBoundaryRegex = true;
      break;
    }
  }

  // Also check for char-level boundary detection logic (indexOf, test, match on single chars)
  const hasCharTest = /\.test\s*\(\s*\w+\s*\[\s*\w+\s*\]/.test(utilSection) ||
                      /\.test\s*\(\s*\w+\.charAt/.test(utilSection);

  if (hasBoundaryRegex || hasCharTest) console.log('OK');
  else console.log('NO_SNAP');
" 2>/dev/null || echo "ERROR")

if [ "$SNAP_RESULT" = "OK" ]; then
    log "PASS: Word boundary snapping logic found"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: No word boundary snapping detected: $SNAP_RESULT"
fi

# ── Structural: anti-stub ────────────────────────────────────────────
# [static] (0.05): File must not be stubbed or truncated
log ""
log "=== STRUCTURAL: anti-stub ==="
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
LINE_COUNT=$(wc -l < "$FILE" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -ge 100 ]; then
    log "PASS: message-part.tsx has $LINE_COUNT lines"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: message-part.tsx has only $LINE_COUNT lines — likely stubbed"
fi

# ── Config: no `any` type in changed code ────────────────────────────
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ af2ccc94
log ""
log "=== CONFIG: no \`any\` type in changed code ==="
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
DIFF=$(cd "$REPO" && git diff HEAD -- packages/ui/src/components/message-part.tsx 2>/dev/null || echo "")
if [ -z "$DIFF" ]; then
    DIFF=$(cd "$REPO" && git diff HEAD~1 -- packages/ui/src/components/message-part.tsx 2>/dev/null || echo "")
fi
ANY_COUNT=$(echo "$DIFF" | grep '^\+' | grep -v '^\+\+\+' | grep -c ':\s*any\b' || true)
if [ "$ANY_COUNT" = "0" ]; then
    log "PASS: No \`any\` types in changed code"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Found $ANY_COUNT \`any\` type usage(s)"
fi

# ── Final score ──────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
log "Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
