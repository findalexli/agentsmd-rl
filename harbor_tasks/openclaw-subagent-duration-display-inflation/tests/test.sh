#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
SCORE=0

pass() { SCORE=$(python3 -c "print(${SCORE} + ${1})"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE: Target file must exist ───────────────────────────────────
if [ ! -f "${REPO}/src/shared/subagents-format.ts" ]; then
  echo "GATE FAIL: src/shared/subagents-format.ts does not exist"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

# ── Helper: extract and evaluate formatDurationCompact ─────────────
# Writes a self-contained Node script that resolves the function
# (following re-exports if needed), strips TS types, evals, and tests
cat > /tmp/test_formatter.js << 'NODEEOF'
const fs = require('fs');
const path = require('path');
const REPO = '/workspace/openclaw';

function loadFunc() {
  const src = fs.readFileSync(REPO + '/src/shared/subagents-format.ts', 'utf8');

  // Check for re-export: export { formatDurationCompact } from '...'
  const reExport = src.match(
    /export\s*\{[^}]*\bformatDurationCompact\b[^}]*\}\s*from\s*['"]([^'"]+)['"]/
  );

  let targetSrc;
  if (reExport) {
    let importPath = reExport[1];
    // Resolve relative to the source file's directory
    let resolved = path.resolve(REPO + '/src/shared', importPath);
    // Try .ts extension
    for (const ext of ['', '.ts', '.js']) {
      const p = resolved + ext;
      if (fs.existsSync(p)) { targetSrc = fs.readFileSync(p, 'utf8'); break; }
    }
    if (!targetSrc) {
      console.log(JSON.stringify({ error: 'REEXPORT_TARGET_NOT_FOUND' }));
      return null;
    }
  } else {
    targetSrc = src;
  }

  // Extract function using brace matching
  const lines = targetSrc.split('\n');
  let start = -1, braceDepth = 0, end = -1, opened = false;
  for (let i = 0; i < lines.length; i++) {
    if (start === -1 && /(?:export\s+)?function\s+formatDurationCompact\b/.test(lines[i])) {
      start = i;
      braceDepth = 0;
    }
    if (start !== -1) {
      for (const ch of lines[i]) {
        if (ch === '{') { braceDepth++; opened = true; }
        if (ch === '}') braceDepth--;
      }
      if (opened && braceDepth === 0) { end = i; break; }
    }
  }

  if (start === -1 || end === -1) {
    console.log(JSON.stringify({ error: 'FUNC_NOT_FOUND' }));
    return null;
  }

  let funcText = lines.slice(start, end + 1).join('\n');
  // Strip TS type annotations: parameter types, return type, const types
  funcText = funcText
    .replace(/export\s+function/, 'function')
    .replace(/(function\s+formatDurationCompact)\s*\(([^)]*)\)\s*(?::\s*[^{]*?)?\s*\{/,
      (_, name, params) => {
        const cleanParams = params.replace(/\?\s*:\s*[^,)]+/g, '').replace(/:\s*[^,)]+/g, '');
        return name + '(' + cleanParams + ') {';
      })
    .replace(/(?:const|let|var)\s+(\w+)\s*:\s*[\w|<>[\]\s]+\s*=/g, 'const $1 =');

  try {
    eval(funcText);
    return eval('formatDurationCompact');
  } catch(e) {
    console.log(JSON.stringify({ error: 'EVAL_ERROR', message: e.message }));
    return null;
  }
}

const fn = loadFunc();
if (!fn) process.exit(0);

// Run test cases and output results
const results = {};
const cases = {
  ms30000: 30000,
  ms5000: 5000,
  ms90000: 90000,
  ms3600000: 3600000,
  ms0: 0,
  msUndef: undefined,
  msNeg: -1000,
};

for (const [key, input] of Object.entries(cases)) {
  try {
    results[key] = { value: fn(input), ok: true };
  } catch(e) {
    results[key] = { value: null, error: e.message, ok: false };
  }
}

console.log(JSON.stringify(results));
NODEEOF

FORMATTER_OUT=$(node /tmp/test_formatter.js 2>/dev/null)
echo "DEBUG formatter results: ${FORMATTER_OUT}"

# Check if we got valid JSON results (not an error)
HAS_ERROR=$(echo "$FORMATTER_OUT" | node -e "
  try {
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(d.error ? 'yes' : 'no');
  } catch(e) { console.log('yes'); }
" 2>/dev/null)

if [ "$HAS_ERROR" = "yes" ]; then
  echo "WARN: Could not extract/eval formatDurationCompact — falling back to structural checks"
  BEHAVIORAL_AVAILABLE=0
else
  BEHAVIORAL_AVAILABLE=1
fi

# ── Behavioral: Fail-to-pass core (0.35) ───────────────────────────
# [pr_diff] (0.35): formatDurationCompact(30000) must show second-level precision
# The buggy code returns "1m" for 30000ms; any correct fix returns "30s" or similar
if [ "$BEHAVIORAL_AVAILABLE" = "1" ]; then
  R30=$(echo "$FORMATTER_OUT" | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    const v = d.ms30000 && d.ms30000.value;
    console.log(v || 'null');
  " 2>/dev/null)
  echo "DEBUG formatDurationCompact(30000) = ${R30}"

  # Must contain "30" and "s" (second indicator), must NOT be "1m"
  if echo "$R30" | grep -q '30' && echo "$R30" | grep -q 's' && ! echo "$R30" | grep -qx '1m'; then
    pass 0.35 "formatDurationCompact(30000) returns second-level precision: ${R30}"
  else
    fail 0.35 "formatDurationCompact(30000) = '${R30}' — expected second-level like '30s'"
  fi
else
  # Structural fallback: buggy pattern must be gone
  if grep -q 'Math.max(1, Math.round.*60_000' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null; then
    fail 0.35 "Buggy Math.max(1, Math.round(ms / 60_000)) still present"
  else
    # Can only give partial credit without behavioral verification
    pass 0.15 "Buggy minute-rounding removed (structural only — partial credit)"
    fail 0.20 "Could not verify actual output behaviorally"
  fi
fi

# ── Behavioral: Extended duration tests (0.15) ─────────────────────
# [pr_diff] (0.15): Multiple durations must format with second-level precision
if [ "$BEHAVIORAL_AVAILABLE" = "1" ]; then
  EXTENDED_OK=0
  EXTENDED_TOTAL=3

  # 5000ms → should contain "5" and "s"
  R5=$(echo "$FORMATTER_OUT" | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(d.ms5000 && d.ms5000.value || 'null');
  " 2>/dev/null)
  if echo "$R5" | grep -q '5' && echo "$R5" | grep -q 's'; then
    EXTENDED_OK=$((EXTENDED_OK + 1))
  fi

  # 90000ms → should contain minute AND second info (e.g. "1m30s", "1m 30s", "90s")
  R90=$(echo "$FORMATTER_OUT" | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(d.ms90000 && d.ms90000.value || 'null');
  " 2>/dev/null)
  # Accept: "1m30s", "1m 30s", "90s", "1:30" — must have second-level info
  if echo "$R90" | grep -qE '(30s|30 s|:30|90s)'; then
    EXTENDED_OK=$((EXTENDED_OK + 1))
  fi

  # 3600000ms → should still return hour-level (pass-to-pass)
  R3600=$(echo "$FORMATTER_OUT" | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(d.ms3600000 && d.ms3600000.value || 'null');
  " 2>/dev/null)
  if echo "$R3600" | grep -qE '(1h|60m|1 h)'; then
    EXTENDED_OK=$((EXTENDED_OK + 1))
  fi

  echo "DEBUG extended: 5s=${R5}, 90s=${R90}, 1h=${R3600} — ${EXTENDED_OK}/${EXTENDED_TOTAL}"

  if [ "$EXTENDED_OK" -ge 2 ]; then
    pass 0.15 "Extended duration formatting correct (${EXTENDED_OK}/${EXTENDED_TOTAL})"
  elif [ "$EXTENDED_OK" -ge 1 ]; then
    pass 0.05 "Partial extended duration formatting (${EXTENDED_OK}/${EXTENDED_TOTAL})"
  else
    fail 0.15 "Extended duration formatting failed (${EXTENDED_OK}/${EXTENDED_TOTAL})"
  fi
else
  fail 0.15 "Extended duration tests skipped (function not evaluable)"
fi

# ── Behavioral: Invalid input handling (0.05) ──────────────────────
# [pr_diff] (0.05): formatDurationCompact(0), formatDurationCompact(undefined) must not crash
if [ "$BEHAVIORAL_AVAILABLE" = "1" ]; then
  INVALID_OK=$(echo "$FORMATTER_OUT" | node -e "
    const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    let ok = 0;
    // These should not have thrown errors
    if (d.ms0 && d.ms0.ok) ok++;
    if (d.msUndef && d.msUndef.ok) ok++;
    if (d.msNeg && d.msNeg.ok) ok++;
    console.log(ok >= 2 ? 'pass' : 'fail');
  " 2>/dev/null)

  if [ "$INVALID_OK" = "pass" ]; then
    pass 0.05 "Invalid inputs (0, undefined, negative) handled without crashing"
  else
    fail 0.05 "Invalid inputs cause errors"
  fi
else
  fail 0.05 "Invalid input test skipped"
fi

# ── Behavioral: Buggy pattern must be gone (0.10) ──────────────────
# [pr_diff] (0.10): The Math.max(1, Math.round(ms / 60_000)) bug must be removed
if ! grep -q 'Math.max(1, Math.round.*60_000' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null; then
  pass 0.10 "Buggy minute-rounding logic removed from subagents-format.ts"
else
  fail 0.10 "Buggy Math.max(1, Math.round(ms / 60_000)) still present"
fi

# ── Pass-to-pass: Other exports still work (0.10) ─────────────────
# [pr_diff] (0.05): formatTokenShort must still be exported
if grep -q 'formatTokenShort' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null; then
  pass 0.05 "formatTokenShort still present in subagents-format.ts"
else
  fail 0.05 "formatTokenShort was accidentally removed"
fi

# [pr_diff] (0.05): truncateLine must still be exported
if grep -q 'truncateLine' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null; then
  pass 0.05 "truncateLine still present in subagents-format.ts"
else
  fail 0.05 "truncateLine was accidentally removed"
fi

# ── Caller undefined handling (0.10) ───────────────────────────────
# [pr_diff] (0.05): subagent-control.ts must handle undefined from formatter
# Accept: ??, ||, ternary, if-check, String(), template with fallback, helper function
CTRL_SRC=$(cat "${REPO}/src/agents/subagent-control.ts" 2>/dev/null || echo "")
if echo "$CTRL_SRC" | grep -Pq 'formatDurationCompact\([^)]*\)\s*(\?\?|\|\|)' || \
   echo "$CTRL_SRC" | grep -Pq 'formatDurationCompact\([^)]*\)\s*!\s*=' || \
   echo "$CTRL_SRC" | grep -q 'formatDurationHuman' || \
   echo "$CTRL_SRC" | grep -Pq '(const|let|var)\s+\w+\s*=\s*formatDurationCompact.*\n.*\?\s' || \
   echo "$CTRL_SRC" | grep -q 'String(formatDurationCompact'; then
  pass 0.05 "subagent-control.ts handles potential undefined from formatter"
else
  # Also accept: if the buggy function was kept inline with "n/a" fallback (still returns string)
  INLINE_SRC=$(cat "${REPO}/src/shared/subagents-format.ts" 2>/dev/null)
  if echo "$INLINE_SRC" | grep -q 'function formatDurationCompact' && echo "$INLINE_SRC" | grep -q '"n/a"\|return.*"n/a"'; then
    pass 0.05 "Inline implementation still returns string fallback — no undefined possible"
  else
    fail 0.05 "subagent-control.ts may not handle undefined from formatter"
  fi
fi

# [pr_diff] (0.05): commands-subagents/shared.ts must handle undefined from formatter
SHARED_SRC=$(cat "${REPO}/src/auto-reply/reply/commands-subagents/shared.ts" 2>/dev/null || echo "")
if echo "$SHARED_SRC" | grep -Pq 'formatDurationCompact\([^)]*\)\s*(\?\?|\|\|)' || \
   echo "$SHARED_SRC" | grep -Pq 'formatDurationCompact\([^)]*\)\s*!\s*=' || \
   echo "$SHARED_SRC" | grep -q 'formatDurationHuman' || \
   echo "$SHARED_SRC" | grep -Pq '(const|let|var)\s+\w+\s*=\s*formatDurationCompact.*\n.*\?\s' || \
   echo "$SHARED_SRC" | grep -q 'String(formatDurationCompact'; then
  pass 0.05 "commands-subagents/shared.ts handles potential undefined from formatter"
else
  if echo "$INLINE_SRC" | grep -q 'function formatDurationCompact' && echo "$INLINE_SRC" | grep -q '"n/a"\|return.*"n/a"'; then
    pass 0.05 "Inline implementation still returns string fallback — no undefined possible"
  else
    fail 0.05 "commands-subagents/shared.ts may not handle undefined from formatter"
  fi
fi

# ── Config-derived: deduplication (0.05) ───────────────────────────
# [agent_config] (0.05): "Keep files concise; extract helpers instead of 'V2' copies." — CLAUDE.md:164
# Must not have a full duplicate of the canonical formatter
FUNC_COUNT=$(grep -c 'function formatDurationCompact' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null || true)
if [ "$FUNC_COUNT" = "0" ]; then
  # Re-export pattern — best approach
  pass 0.05 "No duplicate function — uses re-export or delegation"
elif [ "$FUNC_COUNT" = "1" ]; then
  # Check body size — a thin wrapper (≤8 lines) is OK, a full reimplementation is not
  BODY_LINES=$(node -e "
    const src = require('fs').readFileSync('${REPO}/src/shared/subagents-format.ts','utf8');
    const m = src.match(/function formatDurationCompact[^{]*\{([\s\S]*?)^\}/m);
    if (m) {
      const body = m[1].trim().split('\n').filter(l => l.trim()).length;
      console.log(body);
    } else { console.log(0); }
  " 2>/dev/null)
  if [ "${BODY_LINES:-0}" -le 8 ]; then
    pass 0.05 "Thin wrapper or simplified implementation (${BODY_LINES} lines)"
  else
    fail 0.05 "Full duplicate formatDurationCompact still present (${BODY_LINES} body lines)"
  fi
else
  fail 0.05 "Multiple formatDurationCompact definitions found"
fi

# ── Config-derived: strict typing (0.05) ──────────────────────────
# [agent_config] (0.05): "Prefer strict typing; avoid any." — CLAUDE.md:144
if grep -q ': any' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null; then
  fail 0.05 "Introduced 'any' type in subagents-format.ts"
else
  pass 0.05 "No 'any' types introduced"
fi

# ── Anti-stub (0.10) ──────────────────────────────────────────────
# [pr_diff] (0.10): subagents-format.ts must have substantive content
LINE_COUNT=$(wc -l < "${REPO}/src/shared/subagents-format.ts" 2>/dev/null || echo "0")
HAS_EXPORT=$(grep -c 'export' "${REPO}/src/shared/subagents-format.ts" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -ge 5 ] && [ "$HAS_EXPORT" -ge 2 ]; then
  pass 0.10 "subagents-format.ts has substantive content (${LINE_COUNT} lines, ${HAS_EXPORT} exports)"
else
  fail 0.10 "subagents-format.ts appears stubbed (${LINE_COUNT} lines, ${HAS_EXPORT} exports)"
fi

# ── Finalize ────────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${SCORE} / 1.0"
echo "${SCORE}" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('${SCORE}')
# Compute category scores from actual check results
behavioral = min(score, 0.65)
regression = min(max(score - 0.65, 0), 0.10)
config = min(max(score - 0.75, 0), 0.10)
json.dump({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(json.load(open('/logs/verifier/reward.json')), indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
