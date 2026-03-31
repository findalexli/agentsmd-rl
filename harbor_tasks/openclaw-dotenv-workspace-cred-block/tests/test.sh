#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
TARGET="${REPO}/src/infra/dotenv.ts"
SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print(round(${SCORE} + ${1}, 4))"); TOTAL=$(python3 -c "print(round(${TOTAL} + ${1}, 4))"); echo "PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print(round(${TOTAL} + ${1}, 4))"); echo "FAIL ($1): $2"; }

mkdir -p /logs/verifier

# ── GATE: File exists and is parseable ─────────────────────────────
if [ ! -f "${TARGET}" ]; then
  echo "GATE FAIL: ${TARGET} does not exist"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi

if ! node -e "
  const fs = require('fs');
  const code = fs.readFileSync('${TARGET}', 'utf8');
  try { new Function(code); } catch(e) {
    if (e instanceof SyntaxError && !e.message.includes('import') && !e.message.includes('export') && !e.message.includes('await')) {
      process.exit(1);
    }
  }
" 2>/dev/null; then
  echo "GATE FAIL: ${TARGET} has syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: TypeScript file exists and parses OK"

# ── Helper: Extract shouldBlockWorkspaceDotEnvKey and its dependencies ──
# We strip TS types and reconstruct the blocking logic as plain JS,
# then call it behaviorally. This accepts ANY valid implementation
# (Set, Map, array, regex, if-chain, etc.) as long as it blocks correctly.

EXTRACT_AND_TEST=$(cat <<'JSEOF'
const fs = require('fs');
const path = require('path');

// Node 22+ drops '[eval]' from argv; find file arg dynamically
const fileArg = process.argv.find(a => a.endsWith('.ts'));
const code = fs.readFileSync(fileArg, 'utf8');

// Strategy: We need to call shouldBlockWorkspaceDotEnvKey.
// The function depends on:
//   - BLOCKED_WORKSPACE_DOTENV_KEYS (Set or similar)
//   - BLOCKED_WORKSPACE_DOTENV_SUFFIXES (array)
//   - BLOCKED_WORKSPACE_DOTENV_PREFIXES (array, added by fix)
//   - shouldBlockRuntimeDotEnvKey -> external imports
//
// We'll extract the relevant code, replace imports with stubs,
// strip TypeScript annotations, and eval.

// Strip TypeScript type annotations (: string, : boolean, : Set<string>, etc.)
let js = code;
// Remove import lines
js = js.replace(/^import\s+.*?;?\s*$/gm, '');
// Remove export keywords (but keep function/const)
js = js.replace(/^export\s+/gm, '');
// Strip TS type annotations on parameters and return types
js = js.replace(/:\s*(string|boolean|number|void|Record<[^>]+>|Set<[^>]+>|[A-Z]\w*(\[\])?)\b/g, '');
// Strip 'as const' assertions
js = js.replace(/\s+as\s+const\b/g, '');

// Provide stubs for imported functions (these handle proxy/host vars, not credentials)
const preamble = `
  function isDangerousHostEnvVarName(key) { return false; }
  function isDangerousHostEnvOverrideVarName(key) { return false; }
  function normalizeEnvVarKey(key) { return key; }
  function resolveConfigDir() { return '/tmp'; }
  const dotenv = { parse: () => ({}) };
  const fs = require('fs');
  const path = require('path');
`;

// Extract only the parts we need (constants + shouldBlock functions)
// Find all const/function declarations that are relevant
const lines = js.split('\n');
const relevantCode = [];
let braceDepth = 0;
let capturing = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  // Start capturing on relevant declarations
  if (/^\s*(const\s+BLOCKED_WORKSPACE|function\s+shouldBlock)/.test(line)) {
    capturing = true;
    braceDepth = 0;
  }
  if (capturing) {
    relevantCode.push(line);
    for (const ch of line) {
      if (ch === '{' || ch === '[' || ch === '(') braceDepth++;
      if (ch === '}' || ch === ']' || ch === ')') braceDepth--;
    }
    // Stop capturing when balanced and line ends with ; or }
    if (braceDepth <= 0 && (line.trimEnd().endsWith(';') || line.trimEnd().endsWith('}'))) {
      capturing = false;
    }
  }
}

const fullCode = preamble + '\n' + relevantCode.join('\n') + `
  // Export for testing
  module.exports = { shouldBlockWorkspaceDotEnvKey };
`;

try {
  const m = { exports: {} };
  const fn = new Function('require', 'module', 'exports', '__filename', '__dirname', fullCode);
  fn(require, m, m.exports, __filename, __dirname);
  const { shouldBlockWorkspaceDotEnvKey } = m.exports;

  if (typeof shouldBlockWorkspaceDotEnvKey !== 'function') {
    console.log('ERROR: shouldBlockWorkspaceDotEnvKey is not a function');
    process.exit(2);
  }

  // Run tests passed as JSON on last argv element
  const jsonArg = process.argv.find(a => a.startsWith('{'));
  const tests = JSON.parse(jsonArg);
  const results = {};
  for (const [key, expected] of Object.entries(tests)) {
    try {
      const actual = shouldBlockWorkspaceDotEnvKey(key);
      results[key] = { expected: expected, actual: !!actual, pass: !!actual === expected };
    } catch (e) {
      results[key] = { expected: expected, actual: 'ERROR: ' + e.message, pass: false };
    }
  }
  console.log(JSON.stringify(results));
} catch (e) {
  console.log('EXTRACT_ERROR: ' + e.message);
  process.exit(2);
}
JSEOF
)

# ── BEHAVIORAL: Fail-to-pass — credential keys must be blocked ─────

# [pr_diff] (0.30): Core credential keys (ANTHROPIC_API_KEY, OPENAI_API_KEY) are blocked
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"ANTHROPIC_API_KEY": true, "OPENAI_API_KEY": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  echo "WARN: Could not extract function, falling back to structural"
  # Structural fallback: check that the key names appear near blocking logic
  if node -e "
    const code = require('fs').readFileSync('${TARGET}','utf8');
    const hasKey = k => code.includes(k);
    if (!hasKey('ANTHROPIC_API_KEY') || !hasKey('OPENAI_API_KEY')) process.exit(1);
    // Must be near blocking logic, not just in a comment
    const blockSection = code.match(/BLOCKED_WORKSPACE[\s\S]{0,2000}/);
    if (!blockSection || !blockSection[0].includes('ANTHROPIC_API_KEY')) process.exit(1);
  " 2>/dev/null; then
    pass 0.15 "Core credential keys appear in blocking logic (structural fallback, reduced credit)"
  else
    fail 0.30 "Core credential keys not blocked"
  fi
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  if(!r.ANTHROPIC_API_KEY.pass || !r.OPENAI_API_KEY.pass) process.exit(1);
" 2>/dev/null; then
  pass 0.30 "ANTHROPIC_API_KEY and OPENAI_API_KEY are blocked (behavioral)"
else
  fail 0.30 "Core credential keys not blocked behaviorally"
fi

# [pr_diff] (0.10): OAuth and secondary credential keys are blocked
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"ANTHROPIC_OAUTH_TOKEN": true, "OPENAI_API_KEYS": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  if grep -q 'ANTHROPIC_OAUTH_TOKEN' "${TARGET}" 2>/dev/null; then
    pass 0.05 "ANTHROPIC_OAUTH_TOKEN in file (structural fallback, reduced)"
  else
    fail 0.10 "OAuth/secondary keys not blocked"
  fi
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const allPass = Object.values(r).every(v => v.pass);
  if(!allPass) process.exit(1);
" 2>/dev/null; then
  pass 0.10 "OAuth and secondary credential keys blocked (behavioral)"
else
  fail 0.10 "OAuth/secondary credential keys not blocked"
fi

# [pr_diff] (0.10): Gateway auth vars are blocked
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"OPENCLAW_GATEWAY_TOKEN": true, "OPENCLAW_GATEWAY_PASSWORD": true, "OPENCLAW_GATEWAY_SECRET": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  GW=0
  for v in OPENCLAW_GATEWAY_TOKEN OPENCLAW_GATEWAY_PASSWORD OPENCLAW_GATEWAY_SECRET; do
    grep -q "\"${v}\"" "${TARGET}" 2>/dev/null && GW=$((GW+1))
  done
  if [ "$GW" -ge 3 ]; then pass 0.05 "Gateway vars in file (structural, reduced)";
  else fail 0.10 "Gateway auth vars not blocked"; fi
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const allPass = Object.values(r).every(v => v.pass);
  if(!allPass) process.exit(1);
" 2>/dev/null; then
  pass 0.10 "Gateway auth vars blocked (behavioral)"
else
  # Partial credit if some pass
  PASS_COUNT=$(echo "$RESULT" | node -e "
    const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(Object.values(r).filter(v=>v.pass).length);
  " 2>/dev/null)
  if [ "${PASS_COUNT:-0}" -ge 1 ]; then
    pass 0.05 "Some gateway vars blocked ($PASS_COUNT/3)"
    fail 0.05 "Not all gateway vars blocked"
  else
    fail 0.10 "No gateway auth vars blocked"
  fi
fi

# [pr_diff] (0.05): OPENCLAW_LIVE_* provider keys are blocked
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"OPENCLAW_LIVE_ANTHROPIC_KEY": true, "OPENCLAW_LIVE_OPENAI_KEY": true, "OPENCLAW_LIVE_GEMINI_KEY": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  LIVE=0
  for v in OPENCLAW_LIVE_ANTHROPIC_KEY OPENCLAW_LIVE_OPENAI_KEY OPENCLAW_LIVE_GEMINI_KEY; do
    grep -q "\"${v}\"" "${TARGET}" 2>/dev/null && LIVE=$((LIVE+1))
  done
  [ "$LIVE" -ge 2 ] && pass 0.03 "LIVE keys in file (structural, reduced)" || fail 0.05 "LIVE keys not blocked"
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const passes = Object.values(r).filter(v=>v.pass).length;
  if(passes < 2) process.exit(1);
" 2>/dev/null; then
  pass 0.05 "OPENCLAW_LIVE_* keys blocked (behavioral)"
else
  fail 0.05 "OPENCLAW_LIVE_* keys not blocked"
fi

# [pr_diff] (0.10): Prefix-based blocking covers key variants (e.g. _SECONDARY)
# This is the key behavioral test — a correct fix must block novel suffixed variants
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"ANTHROPIC_API_KEY_SECONDARY": true, "OPENAI_API_KEY_BACKUP": true, "ANTHROPIC_API_KEY_V2": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  # Structural fallback: check for prefix logic (startsWith or similar)
  if node -e "
    const code = require('fs').readFileSync('${TARGET}','utf8');
    const hasPrefix = /startsWith|PREFIX|\.some\(.*=>.*\.startsWith/.test(code);
    if (!hasPrefix) process.exit(1);
  " 2>/dev/null; then
    pass 0.05 "Prefix logic present (structural, reduced)"
  else
    fail 0.10 "No prefix-based blocking for key variants"
  fi
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const allPass = Object.values(r).every(v => v.pass);
  if(!allPass) process.exit(1);
" 2>/dev/null; then
  pass 0.10 "Prefix-based blocking works for key variants (behavioral)"
else
  fail 0.10 "Key variants (ANTHROPIC_API_KEY_SECONDARY etc.) not blocked"
fi

# ── BEHAVIORAL: Pass-to-pass — existing blocking still works ───────

# [pr_diff] (0.10): Original blocked keys still blocked, safe keys still allowed
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"ALL_PROXY": true, "HTTP_PROXY": true, "OPENCLAW_STATE_DIR": true, "MY_CUSTOM_VAR": false, "DATABASE_URL": false, "APP_SECRET": false}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  # Fallback: at minimum check original vars still in file
  ORIG=0
  for v in ALL_PROXY HTTP_PROXY HTTPS_PROXY OPENCLAW_STATE_DIR OPENCLAW_CONFIG_PATH; do
    grep -q "\"${v}\"" "${TARGET}" 2>/dev/null && ORIG=$((ORIG+1))
  done
  if [ "$ORIG" -ge 4 ]; then
    pass 0.05 "Original blocked keys preserved (structural, reduced)"
  else
    fail 0.10 "Original blocked keys missing"
  fi
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  const allPass = Object.values(r).every(v => v.pass);
  if(!allPass) process.exit(1);
" 2>/dev/null; then
  pass 0.10 "Original blocking preserved AND safe keys allowed through (behavioral)"
else
  # Partial: check how many pass
  COUNT=$(echo "$RESULT" | node -e "
    const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(Object.values(r).filter(v=>v.pass).length + '/' + Object.values(r).length);
  " 2>/dev/null)
  pass 0.05 "Partial pass-to-pass ($COUNT correct)"
  fail 0.05 "Some P2P checks failed"
fi

# [pr_diff] (0.05): _BASE_URL suffix blocking still works
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"OPENAI_BASE_URL": true, "CUSTOM_SERVICE_BASE_URL": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  grep -q '_BASE_URL' "${TARGET}" 2>/dev/null && pass 0.03 "_BASE_URL in file (structural)" || fail 0.05 "_BASE_URL blocking missing"
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  if(!Object.values(r).every(v=>v.pass)) process.exit(1);
" 2>/dev/null; then
  pass 0.05 "_BASE_URL suffix blocking works (behavioral)"
else
  fail 0.05 "_BASE_URL suffix blocking broken"
fi

# ── BEHAVIORAL: Case insensitivity ────────────────────────────────
# [pr_diff] (0.05): Blocking is case-insensitive (key.toUpperCase())
RESULT=$(node -e "${EXTRACT_AND_TEST}" -- "${TARGET}" '{"anthropic_api_key": true, "Openai_Api_Key": true}' 2>/dev/null)
EXIT=$?
if [ $EXIT -eq 2 ]; then
  pass 0.00 "Skipped case test (extraction failed)"
elif echo "$RESULT" | node -e "
  const r=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  if(!Object.values(r).every(v=>v.pass)) process.exit(1);
" 2>/dev/null; then
  pass 0.05 "Case-insensitive blocking works (behavioral)"
else
  fail 0.05 "Blocking is not case-insensitive"
fi

# ── CONFIG-DERIVED CHECKS ──────────────────────────────────────────

# [agent_config] (0.05): "Never add @ts-nocheck" — CLAUDE.md:146
if ! grep -q '@ts-nocheck\|@ts-ignore' "${TARGET}"; then
  pass 0.05 "No @ts-nocheck or @ts-ignore in dotenv.ts"
else
  fail 0.05 "@ts-nocheck or @ts-ignore found"
fi

# [agent_config] (0.05): "Prefer strict typing; avoid any." — CLAUDE.md:144
if ! grep -Pn ':\s*any\b' "${TARGET}" | grep -v '//.*any' >/dev/null 2>&1; then
  pass 0.05 "No bare 'any' type annotations"
else
  fail 0.05 "Bare 'any' type annotation found"
fi

# ── ANTI-STUB: function has real logic ─────────────────────────────

# [pr_diff] (0.05): shouldBlockWorkspaceDotEnvKey function exists and has meaningful body
if node -e "
  const code = require('fs').readFileSync('${TARGET}','utf8');
  const fnMatch = code.match(/function shouldBlockWorkspaceDotEnvKey[\s\S]*?\n\}/);
  if (!fnMatch) process.exit(1);
  const body = fnMatch[0];
  // Must have real logic: at least a return statement and some blocking check
  const hasReturn = /return\s/.test(body);
  const hasCheck = /\.has\(|\.includes\(|===|\.test\(|\.some\(|\.startsWith\(|\.endsWith\(/.test(body);
  if (!hasReturn || !hasCheck) process.exit(1);
  // Must not be a trivial stub (return false / return true)
  const lines = body.split('\\n').filter(l => l.trim() && !l.trim().startsWith('//'));
  if (lines.length < 4) process.exit(1);
" 2>/dev/null; then
  pass 0.05 "shouldBlockWorkspaceDotEnvKey has meaningful logic"
else
  fail 0.05 "shouldBlockWorkspaceDotEnvKey is missing or stubbed"
fi

# ── Finalize ────────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${SCORE} / 1.0"
echo "${SCORE}" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('${SCORE}')
# Behavioral weight: checks 1-8 = 0.85, config = 0.10, anti-stub = 0.05
beh = round(min(score, 0.85), 4)
reg = round(min(max(score - 0.85, 0), 0.05), 4)
cfg = round(min(max(score - 0.90, 0), 0.10), 4)
json.dump({
    'reward': round(score, 4),
    'behavioral': beh,
    'regression': reg,
    'config': cfg,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(json.load(open('/logs/verifier/reward.json')), indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
