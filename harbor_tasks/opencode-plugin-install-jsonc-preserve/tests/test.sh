#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
REPO="/workspace/opencode"
INSTALL_TS="$REPO/packages/opencode/src/plugin/install.ts"

log() { echo "$1"; }

mkdir -p /logs/verifier

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): install.ts must parse without syntax errors
log "=== GATE: Syntax check ==="
cd "$REPO/packages/opencode"
if bun build --no-bundle src/plugin/install.ts --outdir /tmp/gate-check 2>/dev/null; then
    log "GATE passed"
else
    log "GATE FAILED: install.ts has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ── Fail-to-pass 1: JSONC comments preserved when adding plugins ───
# [pr_diff] (0.35): Adding a plugin must not strip JSONC comments
log ""
log "=== F2P-1: JSONC comments preserved on add ==="
TOTAL=$(python3 -c "print($TOTAL + 0.35)")

# Copy behavioral test into project test directory
cp /tests/test_add_comments.ts "$REPO/packages/opencode/test/plugin/test_add_comments.ts"
cd "$REPO/packages/opencode"
if bun run test/plugin/test_add_comments.ts 2>&1; then
    log "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.35)")
else
    log "FAIL: JSONC comments were stripped when adding plugins"
fi

# ── Fail-to-pass 2: JSONC comments preserved when force-replacing ──
# [pr_diff] (0.30): Force-replacing a plugin must not strip JSONC comments
log ""
log "=== F2P-2: JSONC comments preserved on force replace ==="
TOTAL=$(python3 -c "print($TOTAL + 0.30)")

cp /tests/test_force_comments.ts "$REPO/packages/opencode/test/plugin/test_force_comments.ts"
cd "$REPO/packages/opencode"
if bun run test/plugin/test_force_comments.ts 2>&1; then
    log "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    log "FAIL: JSONC comments were stripped when force-replacing"
fi

# ── Pass-to-pass: Existing plugin install tests still pass ──────────
# [repo_tests] (0.15): Existing test suite must not regress
log ""
log "=== P2P: Existing plugin install tests ==="
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

# Remove our behavioral test files so they don't interfere
rm -f "$REPO/packages/opencode/test/plugin/test_add_comments.ts"
rm -f "$REPO/packages/opencode/test/plugin/test_force_comments.ts"

cd "$REPO/packages/opencode"
if bun test test/plugin/install.test.ts 2>&1; then
    log "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    log "FAIL: Existing tests regressed"
fi

# ── Config-derived 1: No `any` type in install.ts ───────────────────
# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ afb6abff
log ""
log "=== CONFIG-1: No \`any\` type ==="
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
if ! grep -P ':\s*any\b|<any>' "$INSTALL_TS" 2>/dev/null | grep -v '//.*any' | grep -q 'any'; then
    log "PASS: No \`any\` type found"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Found \`any\` type usage in install.ts"
fi

# ── Config-derived 2: No else statements in install.ts ───────────────
# [agent_config] (0.05): "Avoid `else` statements. Prefer early returns." — AGENTS.md:84 @ afb6abff
log ""
log "=== CONFIG-2: No else statements ==="
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
if ! grep -P '^\s*\} else\b' "$INSTALL_TS" 2>/dev/null | grep -q 'else'; then
    log "PASS: No else statements"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    log "FAIL: Found else statements in install.ts"
fi

# ── Anti-stub: Code must actually use jsonc-parser for targeted edits ─
# [pr_diff] (0.10): Fix must use jsonc-parser targeted edits, not whole-array replacement
log ""
log "=== STRUCTURAL: Uses targeted jsonc-parser edits ==="
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# The fix should NOT have a pattern like modify(text, ["plugin"], out.list, ...)
# where the entire plugin array is replaced in patchOne
PATCH_ONE_SECTION=$(sed -n '/^async function patchOne/,/^}/p' "$INSTALL_TS" 2>/dev/null || echo "")
if [ -z "$PATCH_ONE_SECTION" ]; then
    # Try alternative: function may not start at column 0
    PATCH_ONE_SECTION=$(sed -n '/function patchOne/,/^[^ ]/p' "$INSTALL_TS" 2>/dev/null || echo "")
fi

USES_WHOLE_REPLACE=0
if echo "$PATCH_ONE_SECTION" | grep -q 'modify(text.*\["plugin"\].*out\.list'; then
    USES_WHOLE_REPLACE=1
fi
if echo "$PATCH_ONE_SECTION" | grep -q 'modify(text.*\["plugin"\].*out\['; then
    USES_WHOLE_REPLACE=1
fi

if [ "$USES_WHOLE_REPLACE" = "0" ]; then
    log "PASS: patchOne does not replace the entire plugin array"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL: patchOne still uses whole-array replacement via modify()"
fi

# ── Final score ──────────────────────────────────────────────────────
log ""
log "=== FINAL ==="
FINAL=$(python3 -c "print(round(min(1.0, max(0.0, $SCORE)), 4))")
log "Score: $FINAL (of $TOTAL)"
echo "$FINAL" > /logs/verifier/reward.txt

# Write detailed reward.json
python3 -c "
import json
score = round(min(1.0, max(0.0, $SCORE)), 4)
json.dump({
    'reward': score,
    'behavioral': round(min(0.65, $SCORE), 4),
    'regression': round(min(0.15, max(0, $SCORE - 0.65)), 4),
    'config': round(min(0.10, max(0, $SCORE - 0.80)), 4),
    'structural': round(min(0.10, max(0, $SCORE - 0.90)), 4),
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
