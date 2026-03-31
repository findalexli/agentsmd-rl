#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
SRC="$REPO/src/gateway/embeddings-http.ts"
REWARD=0

pass() { REWARD=$(python3 -c "print(${REWARD} + ${1})"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE: File exists and is parseable TypeScript ──────────────────
if [ ! -f "$SRC" ]; then
  echo "GATE FAIL: $SRC not found"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi

if ! node -e "
  const fs = require('fs');
  const code = fs.readFileSync('${SRC}', 'utf8');
  try { new Function(code); } catch(e) {
    if (e instanceof SyntaxError && !e.message.includes('import') && !e.message.includes('export') && !e.message.includes('await')) {
      process.exit(1);
    }
  }
" 2>/dev/null; then
  echo "GATE FAIL: embeddings-http.ts has syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: TypeScript syntax OK"

# ── Helper: Strip comments and write to temp file for robust checks ─
STRIPPED_FILE=$(mktemp)
node -e "
const fs = require('fs');
const src = fs.readFileSync('${SRC}', 'utf8');
// Remove single-line comments
let s = src.replace(/\/\/.*$/gm, '');
// Remove multi-line comments
s = s.replace(/\/\*[\s\S]*?\*\//g, '');
fs.writeFileSync('${STRIPPED_FILE}', s);
" 2>/dev/null

if [ ! -s "$STRIPPED_FILE" ]; then
  # Fallback: use original source if stripping failed
  cp "$SRC" "$STRIPPED_FILE"
fi

# ── Behavioral: Core fix — requiredOperatorMethod passed to helper ──

# [pr_diff] (0.35): handleOpenAiEmbeddingsHttpRequest must pass
# requiredOperatorMethod to handleGatewayPostJsonEndpoint. This is the core
# bug — without it, the embeddings endpoint has no scope enforcement.
# WHY structural: starting the gateway server requires the full pnpm
# dependency tree and complex test-helper infrastructure that is impractical
# in the scoring container.
# Comment-stripped source is used to prevent gaming via comment injection.
CORE_FIX=0
if grep -Pzo '(?s)handleGatewayPostJsonEndpoint\s*\(\s*req\s*,\s*res\s*,\s*\{[^}]*requiredOperatorMethod[^}]*\}' \
     "$STRIPPED_FILE" >/dev/null 2>&1; then
  pass 0.35 "requiredOperatorMethod in handleGatewayPostJsonEndpoint call (comment-stripped)"
  CORE_FIX=1
else
  fail 0.35 "requiredOperatorMethod NOT found in handleGatewayPostJsonEndpoint call (comment-stripped)"
fi

# [pr_diff] (0.10): The requiredOperatorMethod value must be a string
# referencing a write-gated method. "chat.send" is canonical but any non-empty
# string value is partially accepted.
if [ "$CORE_FIX" -eq 1 ]; then
  if grep -Pzo '(?s)handleGatewayPostJsonEndpoint\s*\(\s*req\s*,\s*res\s*,\s*\{[^}]*requiredOperatorMethod\s*:\s*"chat\.send"' \
       "$STRIPPED_FILE" >/dev/null 2>&1; then
    pass 0.10 "requiredOperatorMethod set to 'chat.send' (canonical write-gated method)"
  elif grep -Pzo '(?s)handleGatewayPostJsonEndpoint[^}]*requiredOperatorMethod\s*:\s*"[^"]+"' \
       "$STRIPPED_FILE" >/dev/null 2>&1; then
    pass 0.05 "requiredOperatorMethod set to a method string (partial: not canonical)"
    fail 0.05 "requiredOperatorMethod is not 'chat.send'"
  elif grep -Pzo '(?s)handleGatewayPostJsonEndpoint[^}]*requiredOperatorMethod\s*:\s*\w' \
       "$STRIPPED_FILE" >/dev/null 2>&1; then
    pass 0.05 "requiredOperatorMethod set to a variable reference (partial)"
    fail 0.05 "requiredOperatorMethod should be 'chat.send' string literal"
  else
    fail 0.10 "requiredOperatorMethod value not found in call"
  fi
else
  fail 0.10 "requiredOperatorMethod value check skipped (core fix not detected)"
fi

# [pr_diff] (0.15): Alternative fix detection — if the agent added direct
# scope enforcement (resolveGatewayRequestedOperatorScopes /
# authorizeOperatorScopesForMethod / manual 403) without requiredOperatorMethod,
# that's also valid. Only awarded if primary checks didn't already pass.
if [ "$CORE_FIX" -eq 0 ]; then
  ALT_SCOPE=$(grep -c 'resolveGatewayRequestedOperatorScopes\|authorizeOperatorScopesForMethod' \
       "$STRIPPED_FILE" 2>/dev/null) || ALT_SCOPE=0
  ALT_REJECT=$(grep -c '403\|forbidden\|Forbidden\|unauthorized\|Unauthorized' \
       "$STRIPPED_FILE" 2>/dev/null) || ALT_REJECT=0
  if [ "$ALT_SCOPE" -gt 0 ] && [ "$ALT_REJECT" -gt 0 ]; then
    pass 0.15 "Alternative scope enforcement: direct scope check + rejection"
  elif [ "$ALT_SCOPE" -gt 0 ]; then
    pass 0.05 "Alternative scope enforcement: scope function called but no rejection found"
    fail 0.10 "Missing 403/forbidden rejection for unauthorized callers"
  else
    fail 0.15 "No scope enforcement mechanism found in embeddings handler"
  fi
else
  # Primary fix found — auto-award alternative path points
  pass 0.15 "Primary fix detected; alternative check not needed (auto-awarded)"
fi

# ── Anti-stub: function body must be substantial ─────────────────────

# [pr_diff] (0.10): The handler function must contain real logic — not
# just a return statement or empty body. We count non-blank, non-brace lines
# in the function body from comment-stripped source.
FUNC_LINES=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('${STRIPPED_FILE}', 'utf8');
// Find the function and count meaningful lines
const match = src.match(/async\s+function\s+handleOpenAiEmbeddingsHttpRequest[\s\S]*?(?=\nexport|\n(?:async\s+)?function\s|$)/);
if (!match) { process.stdout.write('0'); process.exit(0); }
const body = match[0];
const lines = body.split('\n').filter(l => {
  const t = l.trim();
  return t.length > 0 && t !== '{' && t !== '}' && t !== '});' && t !== ');';
});
process.stdout.write(String(lines.length));
" 2>/dev/null || echo "0")

if [ "$FUNC_LINES" -gt 8 ]; then
  pass 0.10 "Handler function has $FUNC_LINES meaningful lines (not a stub)"
else
  fail 0.10 "Handler function has only $FUNC_LINES meaningful lines (possible stub)"
fi

# ── Pass-to-pass: existing behavior must not break ───────────────────

# [pr_diff] (0.05): handleOpenAiEmbeddingsHttpRequest export still exists
if grep -q 'export.*async.*function.*handleOpenAiEmbeddingsHttpRequest' "$SRC"; then
  pass 0.05 "handleOpenAiEmbeddingsHttpRequest export still exists"
else
  # Also accept named export at bottom: export { handleOpenAiEmbeddingsHttpRequest }
  if grep -q 'handleOpenAiEmbeddingsHttpRequest' "$SRC" 2>/dev/null; then
    pass 0.05 "handleOpenAiEmbeddingsHttpRequest still present (non-standard export)"
  else
    fail 0.05 "handleOpenAiEmbeddingsHttpRequest missing entirely"
  fi
fi

# [pr_diff] (0.05): pathname still set to /v1/embeddings
if grep -q '/v1/embeddings' "$STRIPPED_FILE"; then
  pass 0.05 "pathname /v1/embeddings still present"
else
  fail 0.05 "pathname /v1/embeddings missing or changed"
fi

# ── Config-derived checks ────────────────────────────────────────────

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144
ANY_COUNT=$(grep -cE ':\s*any\b|<any>|as\s+any\b' "$SRC" 2>/dev/null) || ANY_COUNT=0
if [ "$ANY_COUNT" -eq 0 ]; then
  pass 0.05 "No explicit 'any' types in embeddings-http.ts"
else
  fail 0.05 "Found $ANY_COUNT explicit 'any' type(s) in embeddings-http.ts"
fi

# [agent_config] (0.05): "Never add @ts-nocheck" — CLAUDE.md:146
if ! grep -q '@ts-nocheck' "$SRC" 2>/dev/null; then
  pass 0.05 "No @ts-nocheck in embeddings-http.ts"
else
  fail 0.05 "@ts-nocheck found in embeddings-http.ts"
fi

# ── Cleanup ──────────────────────────────────────────────────────────
rm -f "$STRIPPED_FILE"

# ── Finalize ─────────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${REWARD} / 1.0"
echo "${REWARD}" > /logs/verifier/reward.txt

python3 -c "
import json
score = ${REWARD}
# behavioral = core fix (0.35) + value (0.10) + alt (0.15) + anti-stub (0.10) = 0.70
# regression = p2p (0.10)
# config = 0.10
behavioral = min(max(0, score - 0.20), 0.70)
regression = min(max(0, score - behavioral), 0.10)
config = min(max(0, score - behavioral - regression), 0.10)
j = {
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(j, f)
print(json.dumps(j, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
