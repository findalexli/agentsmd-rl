#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
SYSTEM_TS="$REPO/packages/opencode/src/session/system.ts"
PROMPT_DIR="$REPO/packages/opencode/src/session/prompt"

BEHAVIORAL=0
REGRESSION=0
CONFIG_SCORE=0

log() { echo "$1"; }
mkdir -p /logs/verifier

# ── GATE: system.ts must exist and be parseable ──────────────────────
# [pr_diff] (0.00): system.ts must be valid TypeScript
log "=== GATE: system.ts exists ==="
if [ ! -f "$SYSTEM_TS" ]; then
    log "GATE FAILED: system.ts missing"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! node -e "require('fs').readFileSync('$SYSTEM_TS', 'utf8')" 2>/dev/null; then
    log "GATE FAILED: system.ts unreadable"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE passed"

# ── Build behavioral routing tester ──────────────────────────────────
# Patches system.ts: replaces prompt imports with string markers, removes
# other imports, strips export keywords, appends test harness, then runs
# with Bun (which handles TypeScript natively).
cat > /tmp/build_route_test.ts <<'BUILDSCRIPT'
import { readFileSync, writeFileSync } from "fs"

const systemPath = process.argv[2]!

let src = readFileSync(systemPath, "utf8")

// Replace prompt file imports with string markers
src = src.replace(
  /import\s+(\w+)\s+from\s+["']\.\/prompt\/([\w.-]+?)(?:\.txt)?["']\s*;?/g,
  (_: string, varName: string, promptName: string) => {
    const tag = promptName.toUpperCase().replace(/[^A-Z0-9]/g, "_")
    return `const ${varName} = "__PROMPT_${tag}__";`
  }
)

// Remove type-only imports
src = src.replace(/import\s+type\b[^;]*;?\s*/g, "")
// Remove remaining imports (value imports from packages)
src = src.replace(/^import\b[^;]*;?\s*$/gm, "")
// Remove export keywords so functions become module-scoped
src = src.replace(/\bexport\s+/g, "")

// Append test harness that calls provider() with various model IDs
src += `
;(() => {
  const R: Record<string, string> = {};
  const models = [
    "gpt-5.4", "gpt-5", "gpt-3.5-turbo",
    "codex-mini", "gpt-codex-test",
    "gpt-4o", "o1-mini", "o3-mini",
    "gemini-2.0-flash", "claude-sonnet-4-20250514"
  ];
  for (const id of models) {
    try {
      const fn = typeof provider === "function" ? provider : null;
      if (!fn) { R[id] = "NO_PROVIDER"; continue; }
      const r = fn({ api: { id } });
      R[id] = Array.isArray(r) && r.length > 0 ? String(r[0])
            : typeof r === "string" ? r
            : "NO_RESULT";
    } catch (e: any) {
      R[id] = "ERROR:" + (e?.message?.slice(0, 80) ?? "");
    }
  }
  console.log(JSON.stringify(R));
})();
`

writeFileSync("/tmp/patched_system.ts", src)
BUILDSCRIPT

log ""
log "=== Building and running behavioral routing tests ==="
bun run /tmp/build_route_test.ts "$SYSTEM_TS" 2>/dev/null
ROUTE_JSON=$(bun run /tmp/patched_system.ts 2>/dev/null || echo '{}')
echo "$ROUTE_JSON" > /tmp/route_results.json
log "Routing results: $ROUTE_JSON"

# Helper: extract routing result for a model ID
get_route() {
    python3 -c "
import json, sys
try:
    with open('/tmp/route_results.json') as f:
        data = json.load(f)
    print(data.get('$1', 'MISSING'))
except Exception:
    print('PARSE_ERROR')
" 2>/dev/null
}

# ── F2P-1 (0.40): gpt-5.4 must NOT get codex prompt ─────────────────
# [pr_diff] (0.40): Core bug — generic GPT models routed to wrong prompt
log ""
log "=== F2P-1: gpt-5.4 must not get codex prompt ==="
R_GPT54=$(get_route "gpt-5.4")
log "  gpt-5.4 → $R_GPT54"
if echo "$R_GPT54" | grep -qi "ERROR\|PARSE_ERROR\|MISSING\|NO_PROVIDER"; then
    log "FAIL: Could not evaluate routing for gpt-5.4"
elif echo "$R_GPT54" | grep -qi "CODEX"; then
    log "FAIL: gpt-5.4 still gets codex prompt (the bug)"
else
    log "PASS: gpt-5.4 does not get codex prompt"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.40)")
fi

# ── F2P-2 (0.17): Second generic GPT model also not codex ────────────
# [pr_diff] (0.17): Fix must be general, not just for "gpt-5.4" specifically
log ""
log "=== F2P-2: gpt-5 also must not get codex prompt ==="
R_GPT5=$(get_route "gpt-5")
log "  gpt-5 → $R_GPT5"
if echo "$R_GPT5" | grep -qi "ERROR\|PARSE_ERROR\|MISSING\|NO_PROVIDER"; then
    log "FAIL: Could not evaluate routing for gpt-5"
elif echo "$R_GPT5" | grep -qi "CODEX"; then
    log "FAIL: gpt-5 still gets codex prompt"
else
    log "PASS: gpt-5 does not get codex prompt"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.17)")
fi

# ── F2P-3 (0.10): gpt-5.4 gets a dedicated prompt (not default) ─────
# [pr_diff] (0.10): A dedicated GPT prompt must exist, not just fallback
log ""
log "=== F2P-3: gpt-5.4 gets dedicated prompt, not default ==="
if echo "$R_GPT54" | grep -qi "ERROR\|PARSE_ERROR\|MISSING\|NO_PROVIDER\|NO_RESULT"; then
    log "FAIL: Could not evaluate routing"
elif echo "$R_GPT54" | grep -qi "DEFAULT"; then
    log "FAIL: gpt-5.4 falls through to default prompt (should have dedicated GPT prompt)"
elif echo "$R_GPT54" | grep -qi "CODEX"; then
    log "FAIL: gpt-5.4 gets codex prompt"
else
    log "PASS: gpt-5.4 routed to a dedicated prompt ($R_GPT54)"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.10)")
fi

# ── P2P-1 (0.08): Existing model routing preserved (behavioral) ──────
# [pr_diff] (0.08): gpt-4, gemini, claude routing must still work
log ""
log "=== P2P-1: Existing model routing preserved ==="
P2P_OK=0
P2P_TOTAL=3

R_GPT4=$(get_route "gpt-4o")
R_GEMINI=$(get_route "gemini-2.0-flash")
R_CLAUDE=$(get_route "claude-sonnet-4-20250514")

if echo "$R_GPT4" | grep -qi "BEAST"; then
    P2P_OK=$((P2P_OK + 1))
    log "  gpt-4o → BEAST ✓"
else
    log "  gpt-4o → $R_GPT4 (expected BEAST) ✗"
fi

if echo "$R_GEMINI" | grep -qi "GEMINI"; then
    P2P_OK=$((P2P_OK + 1))
    log "  gemini → GEMINI ✓"
else
    log "  gemini → $R_GEMINI (expected GEMINI) ✗"
fi

if echo "$R_CLAUDE" | grep -qi "ANTHROPIC"; then
    P2P_OK=$((P2P_OK + 1))
    log "  claude → ANTHROPIC ✓"
else
    log "  claude → $R_CLAUDE (expected ANTHROPIC) ✗"
fi

if [ "$P2P_OK" -eq "$P2P_TOTAL" ]; then
    log "PASS: All existing model routing preserved"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.08)")
else
    PARTIAL=$(python3 -c "print(round(0.08 * $P2P_OK / $P2P_TOTAL, 4))")
    log "PARTIAL: $P2P_OK/$P2P_TOTAL existing routes preserved"
    REGRESSION=$(python3 -c "print($REGRESSION + $PARTIAL)")
fi

# ── F2P-4 (0.07): GPT prompt file exists with meaningful content ─────
# [pr_diff] (0.07): A new prompt file must be created for GPT models
log ""
log "=== F2P-4: GPT prompt file exists ==="
GPT_PROMPT=$(find "$PROMPT_DIR" -maxdepth 1 -name "gpt*" -type f 2>/dev/null | head -1)
if [ -n "$GPT_PROMPT" ] && [ -s "$GPT_PROMPT" ]; then
    CHARS=$(wc -c < "$GPT_PROMPT")
    if [ "$CHARS" -ge 50 ]; then
        log "PASS: GPT prompt file exists at $GPT_PROMPT ($CHARS chars)"
        BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.07)")
    else
        log "FAIL: GPT prompt file too short ($CHARS chars)"
    fi
else
    log "FAIL: No GPT prompt file found in $PROMPT_DIR"
fi

# ── P2P-2 (0.04): GPT prompt is distinct from codex prompt ───────────
# [pr_diff] (0.04): The GPT prompt must not be a near-copy of codex
log ""
log "=== P2P-2: GPT prompt distinct from codex ==="
if [ -n "$GPT_PROMPT" ] && [ -f "$PROMPT_DIR/codex.txt" ]; then
    SIMILARITY=$(python3 -c "
import difflib
with open('$GPT_PROMPT') as f: gpt = f.read()
with open('$PROMPT_DIR/codex.txt') as f: codex = f.read()
print(f'{difflib.SequenceMatcher(None, gpt, codex).ratio():.2f}')
" 2>/dev/null)
    if [ -n "$SIMILARITY" ]; then
        IS_COPY=$(python3 -c "print('yes' if float('$SIMILARITY') > 0.90 else 'no')")
        if [ "$IS_COPY" = "no" ]; then
            log "PASS: GPT prompt distinct from codex (similarity: $SIMILARITY)"
            REGRESSION=$(python3 -c "print($REGRESSION + 0.04)")
        else
            log "FAIL: GPT prompt too similar to codex ($SIMILARITY)"
        fi
    else
        log "FAIL: Could not compare prompts"
    fi
else
    log "FAIL: Missing prompt file(s) for comparison"
fi

# ── CONFIG-1 (0.05): No 'any' type in system.ts ──────────────────────
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:28 @ 17e8f577
log ""
log "=== CONFIG-1: No 'any' type ==="
ANY_COUNT=$(grep -c ': any' "$SYSTEM_TS" 2>/dev/null || echo "0")
if [ "$ANY_COUNT" -eq 0 ]; then
    log "PASS: No ': any' in system.ts"
    CONFIG_SCORE=$(python3 -c "print($CONFIG_SCORE + 0.05)")
else
    log "FAIL: Found $ANY_COUNT uses of ': any'"
fi

# ── CONFIG-2 (0.05): No else statements in provider function ─────────
# [agent_config] (0.05): "Avoid else statements. Prefer early returns." — AGENTS.md:71 @ 17e8f577
log ""
log "=== CONFIG-2: No else in provider ==="
PROVIDER_BODY=$(python3 -c "
import re
with open('$SYSTEM_TS') as f:
    src = f.read()
# Find provider function body using brace matching
start = src.find('function provider')
if start == -1:
    print('')
else:
    brace = src.index('{', start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == '{': depth += 1
        elif src[i] == '}': depth -= 1
        if depth == 0:
            print(src[brace:i+1])
            break
" 2>/dev/null)
if echo "$PROVIDER_BODY" | grep -qw 'else' 2>/dev/null; then
    log "FAIL: provider function uses else statements"
else
    log "PASS: No else in provider"
    CONFIG_SCORE=$(python3 -c "print($CONFIG_SCORE + 0.05)")
fi

# ── Final score ───────────────────────────────────────────────────────
log ""
log "=== RESULTS ==="
SCORE=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG_SCORE, 4))")
log "Score: $SCORE / 1.00"
log "  Behavioral: $BEHAVIORAL"
log "  Regression: $REGRESSION"
log "  Config:     $CONFIG_SCORE"

echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
print(json.dumps({
    'reward': round($BEHAVIORAL + $REGRESSION + $CONFIG_SCORE, 4),
    'behavioral': round($BEHAVIORAL, 4),
    'regression': round($REGRESSION, 4),
    'config': round($CONFIG_SCORE, 4)
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
