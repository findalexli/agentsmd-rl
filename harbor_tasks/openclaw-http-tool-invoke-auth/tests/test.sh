#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=100
REPO="/workspace/openclaw"
LOGDIR="/logs/verifier"
mkdir -p "$LOGDIR" 2>/dev/null || true

echo "=== openclaw-http-tool-invoke-auth grading ==="

# ─────────────────────────────────────────────────────────
# GATE (0.00): TypeScript syntax check — abort on failure
# ─────────────────────────────────────────────────────────
echo "[GATE] TypeScript syntax check on modified files..."
GATE_PASS=true
for f in src/gateway/tools-invoke-http.ts src/security/dangerous-tools.ts; do
  if [[ -f "$REPO/$f" ]]; then
    if ! node -e "
      const fs = require('fs');
      const code = fs.readFileSync('$REPO/$f', 'utf8');
      try {
        require('esbuild').transformSync(code, { loader: 'ts' });
        process.exit(0);
      } catch(e) {
        console.error(e.message);
        process.exit(1);
      }
    " 2>/dev/null; then
      echo "  FAIL: $f has syntax errors"
      GATE_PASS=false
    fi
  fi
done

if [[ "$GATE_PASS" == "false" ]]; then
  echo "GATE FAILED — aborting"
  echo "0.0" > "$LOGDIR/reward.txt" 2>/dev/null || echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi
echo "  GATE: PASS"

# ─────────────────────────────────────────────────────────
# FAIL-TO-PASS BEHAVIORAL (0.60 total)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.30): HTTP deny list includes high-risk execution tools
# The fix adds exec, spawn, shell, fs_write, fs_delete, fs_move, apply_patch, nodes
# to DEFAULT_GATEWAY_HTTP_TOOL_DENY. We verify by transpiling and importing the module.
echo "[F2P] Checking deny list includes high-risk tools..."
DENY_SCORE=0
DENY_CHECK=$(node -e "
  try {
    const esbuild = require('esbuild');
    const result = esbuild.buildSync({
      entryPoints: ['$REPO/src/security/dangerous-tools.ts'],
      bundle: false,
      write: false,
      format: 'cjs',
      loader: { '.ts': 'ts' },
    });
    const code = new TextDecoder().decode(result.outputFiles[0].contents);
    const mod = { exports: {} };
    const fn = new Function('exports', 'require', 'module', code);
    fn(mod.exports, require, mod);
    const deny = mod.exports.DEFAULT_GATEWAY_HTTP_TOOL_DENY || [];
    const required = ['exec', 'spawn', 'shell', 'fs_write', 'fs_delete', 'fs_move', 'apply_patch', 'nodes'];
    const missing = required.filter(t => !deny.includes(t));
    console.log(JSON.stringify({ missing, total: deny.length }));
  } catch(e) {
    console.log(JSON.stringify({ missing: ['all'], total: 0, error: e.message }));
  }
" 2>/dev/null || echo '{"missing":["all"],"total":0}')

MISSING=$(echo "$DENY_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).missing.length)}catch(e){console.log(8)}" 2>/dev/null || echo "8")
if [[ "$MISSING" == "0" ]]; then
  echo "  PASS: All 8 high-risk tools in deny list"
  DENY_SCORE=30
else
  PRESENT=$((8 - MISSING))
  DENY_SCORE=$((PRESENT * 30 / 8))
  echo "  PARTIAL: $PRESENT/8 high-risk tools in deny list"
fi
SCORE=$((SCORE + DENY_SCORE))

# [pr_diff] (0.20): Scope authorization and 403 in handler (transpiled, comments stripped)
# The handler must perform scope authorization and return 403 for unauthorized requests.
# We transpile the TS to JS, strip ALL comments, then check executable code.
echo "[F2P] Checking scope authorization in transpiled handler (comment-stripped)..."
SCOPE_SCORE=0
SCOPE_CHECK=$(node -e "
  try {
    const esbuild = require('esbuild');
    const result = esbuild.buildSync({
      entryPoints: ['$REPO/src/gateway/tools-invoke-http.ts'],
      bundle: false,
      write: false,
      format: 'esm',
      loader: { '.ts': 'ts' },
    });
    const code = new TextDecoder().decode(result.outputFiles[0].contents);
    // Strip single-line and multi-line comments from transpiled output
    const stripped = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    // Check 1: handler sends a 403 response (any correct fix must do this)
    const has403 = /403/.test(stripped);

    // Check 2: some form of scope resolution or authorization call in executable code
    // Accept broad patterns: resolveScopes, authorizeScopes, requestedScopes, scopeAuth,
    // x-openclaw-scopes header read, or any scope-check pattern
    const hasScopeLogic = (
      /[Ss]cope/.test(stripped) &&
      (/authorize|resolve|allowed|missing/i.test(stripped))
    );

    // Check 3: the 403 is associated with a forbidden/scope error (not just any 403)
    const hasForbiddenContext = /forbidden|missing.scope|insufficient.*scope|scope.*required/i.test(stripped);

    console.log(JSON.stringify({ has403, hasScopeLogic, hasForbiddenContext }));
  } catch(e) {
    console.log(JSON.stringify({ has403: false, hasScopeLogic: false, hasForbiddenContext: false, error: e.message }));
  }
" 2>/dev/null || echo '{"has403":false,"hasScopeLogic":false,"hasForbiddenContext":false}')

S_403=$(echo "$SCOPE_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).has403)}catch(e){console.log(false)}" 2>/dev/null)
S_SCOPE=$(echo "$SCOPE_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).hasScopeLogic)}catch(e){console.log(false)}" 2>/dev/null)
S_FORBIDDEN=$(echo "$SCOPE_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).hasForbiddenContext)}catch(e){console.log(false)}" 2>/dev/null)

if [[ "$S_403" == "true" && "$S_SCOPE" == "true" && "$S_FORBIDDEN" == "true" ]]; then
  echo "  PASS: Scope authorization with 403 forbidden response in executable code"
  SCOPE_SCORE=20
elif [[ "$S_403" == "true" && "$S_SCOPE" == "true" ]]; then
  echo "  PARTIAL: 403 + scope logic but no forbidden context"
  SCOPE_SCORE=14
elif [[ "$S_403" == "true" ]]; then
  echo "  PARTIAL: 403 response exists but scope logic incomplete"
  SCOPE_SCORE=7
else
  echo "  FAIL: No scope authorization found in executable code"
fi
SCORE=$((SCORE + SCOPE_SCORE))

# [pr_diff] (0.15): Owner-only tool filtering in handler (transpiled, comments stripped)
# HTTP surface must filter out owner-only tools (isOwner=false).
echo "[F2P] Checking owner-only tool filtering in transpiled handler..."
OWNER_SCORE=0
OWNER_CHECK=$(node -e "
  try {
    const esbuild = require('esbuild');
    const result = esbuild.buildSync({
      entryPoints: ['$REPO/src/gateway/tools-invoke-http.ts'],
      bundle: false,
      write: false,
      format: 'esm',
      loader: { '.ts': 'ts' },
    });
    const code = new TextDecoder().decode(result.outputFiles[0].contents);
    const stripped = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    // Accept multiple valid approaches:
    // 1. applyOwnerOnlyToolPolicy(tools, false)
    // 2. tools.filter(t => !t.ownerOnly)
    // 3. Any filtering referencing 'owner' with false/negation
    const hasOwnerPolicy = /applyOwnerOnlyToolPolicy/.test(stripped);
    const hasOwnerFilter = /owner[Oo]nly/.test(stripped) || /ownerFiltered/.test(stripped);
    const hasFalseOrNegation = /,\s*false\s*\)/.test(stripped) || /!\s*\w+\.owner/.test(stripped) || /owner.*===?\s*false/.test(stripped);

    // Either the dedicated policy function OR manual owner filtering
    const ownerHandled = hasOwnerPolicy || (hasOwnerFilter && hasFalseOrNegation);

    console.log(JSON.stringify({ hasOwnerPolicy, hasOwnerFilter, hasFalseOrNegation, ownerHandled }));
  } catch(e) {
    console.log(JSON.stringify({ ownerHandled: false, error: e.message }));
  }
" 2>/dev/null || echo '{"ownerHandled":false}')

O_HANDLED=$(echo "$OWNER_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).ownerHandled)}catch(e){console.log(false)}" 2>/dev/null)

if [[ "$O_HANDLED" == "true" ]]; then
  echo "  PASS: Owner-only tool filtering present in executable code"
  OWNER_SCORE=15
else
  echo "  FAIL: No owner-only filtering in executable code"
fi
SCORE=$((SCORE + OWNER_SCORE))

# ─────────────────────────────────────────────────────────
# PASS-TO-PASS REGRESSION (0.10)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.10): Existing deny entries still present
echo "[P2P] Checking existing deny entries not removed..."
P2P_SCORE=0
EXISTING_CHECK=$(node -e "
  try {
    const esbuild = require('esbuild');
    const result = esbuild.buildSync({
      entryPoints: ['$REPO/src/security/dangerous-tools.ts'],
      bundle: false,
      write: false,
      format: 'cjs',
      loader: { '.ts': 'ts' },
    });
    const code = new TextDecoder().decode(result.outputFiles[0].contents);
    const mod = { exports: {} };
    const fn = new Function('exports', 'require', 'module', code);
    fn(mod.exports, require, mod);
    const deny = mod.exports.DEFAULT_GATEWAY_HTTP_TOOL_DENY || [];
    const originals = ['sessions_spawn', 'sessions_send', 'cron', 'gateway', 'whatsapp_login'];
    const missing = originals.filter(t => !deny.includes(t));
    console.log(missing.length);
  } catch(e) { console.log('5'); }
" 2>/dev/null || echo "5")

if [[ "$EXISTING_CHECK" == "0" ]]; then
  echo "  PASS: All original deny entries preserved"
  P2P_SCORE=10
else
  echo "  FAIL: Some original deny entries missing ($EXISTING_CHECK)"
fi
SCORE=$((SCORE + P2P_SCORE))

# ─────────────────────────────────────────────────────────
# UPSTREAM TEST SUITE (0.15)
# ─────────────────────────────────────────────────────────

echo "[UPSTREAM] Running project vitest on tools-invoke-http tests..."
UPSTREAM_SCORE=0
cd "$REPO"
# Try running vitest on test files for this handler
VITEST_OUTPUT=""
VITEST_EXIT=1
for testfile in src/gateway/tools-invoke-http.test.ts src/gateway/tools-invoke-http.cron-regression.test.ts; do
  if [[ -f "$testfile" ]]; then
    VITEST_OUTPUT=$(timeout 90 npx vitest run "$testfile" --reporter=verbose 2>&1 || true)
    VITEST_EXIT=${PIPESTATUS[0]:-$?}
    break
  fi
done

# Also try running any test that mentions tools-invoke
if [[ "$VITEST_EXIT" != "0" ]]; then
  VITEST_OUTPUT=$(timeout 90 npx vitest run --reporter=verbose 2>&1 | tail -30 || true)
  VITEST_EXIT=${PIPESTATUS[0]:-$?}
fi

if [[ "$VITEST_EXIT" == "0" ]]; then
  echo "  PASS: Upstream vitest suite passes"
  UPSTREAM_SCORE=15
else
  echo "  FAIL: Upstream vitest failed or no tests found"
  echo "  Output tail: $(echo "$VITEST_OUTPUT" | tail -5)"
fi
cd /
SCORE=$((SCORE + UPSTREAM_SCORE))

# ─────────────────────────────────────────────────────────
# STRUCTURAL / ANTI-STUB (0.10)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.05): dangerous-tools.ts deny list is not a stub (>= 10 entries)
echo "[STRUCT] Checking dangerous-tools.ts is not a stub..."
STUB_SCORE=0
DENY_TOTAL=$(echo "$DENY_CHECK" | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');try{console.log(JSON.parse(d).total)}catch(e){console.log(0)}" 2>/dev/null || echo "0")

if [[ "$DENY_TOTAL" -ge 10 ]]; then
  echo "  PASS: Deny list has $DENY_TOTAL entries (>= 10)"
  STUB_SCORE=5
elif [[ "$DENY_TOTAL" -ge 5 ]]; then
  echo "  PARTIAL: Deny list has $DENY_TOTAL entries"
  STUB_SCORE=2
else
  echo "  FAIL: Deny list too short ($DENY_TOTAL entries)"
fi
SCORE=$((SCORE + STUB_SCORE))

# [agent_config] (0.05): "Add brief code comments for tricky or non-obvious logic" — CLAUDE.md:163
echo "[CONFIG] Checking comments on security-critical logic..."
COMMENT_SCORE=0
HANDLER_FILE="$REPO/src/gateway/tools-invoke-http.ts"
if [[ -f "$HANDLER_FILE" ]]; then
  # Check for at least one comment near security-critical authorization logic
  # Use grep on original source (comments ARE the target here)
  HAS_COMMENT=$(grep -cE '//.*\b(scope|owner|HTTP|bearer|identity|authorization|deny|filter)\b' "$HANDLER_FILE" 2>/dev/null || echo "0")
  if [[ "$HAS_COMMENT" -gt 0 ]]; then
    echo "  PASS: Comments present on security-critical logic"
    COMMENT_SCORE=5
  else
    echo "  FAIL: No comments on scope/owner authorization logic"
  fi
fi
SCORE=$((SCORE + COMMENT_SCORE))

# ─────────────────────────────────────────────────────────
# FINAL SCORE
# ─────────────────────────────────────────────────────────

FINAL=$(python3 -c "print(f'{$SCORE / $TOTAL:.4f}')" 2>/dev/null || echo "0.0")
echo ""
echo "=== FINAL SCORE: $SCORE / $TOTAL = $FINAL ==="

# Write reward files
mkdir -p "$(dirname "$LOGDIR/reward.txt")" 2>/dev/null || true
echo "$FINAL" > "$LOGDIR/reward.txt" 2>/dev/null || echo "$FINAL" > /logs/verifier/reward.txt

# Detailed breakdown
python3 -c "
import json
score = $SCORE / $TOTAL
reward = {
    'reward': round(score, 4),
    'behavioral': round(($DENY_SCORE + $SCOPE_SCORE + $OWNER_SCORE) / $TOTAL, 4),
    'regression': round($P2P_SCORE / $TOTAL, 4),
    'upstream': round($UPSTREAM_SCORE / $TOTAL, 4),
    'structural': round($STUB_SCORE / $TOTAL, 4),
    'config': round($COMMENT_SCORE / $TOTAL, 4),
}
with open('$LOGDIR/reward.json', 'w') as f:
    json.dump(reward, f, indent=2)
print(json.dumps(reward, indent=2))
" 2>/dev/null || true

# Also write to legacy locations
cp "$LOGDIR/reward.txt" "/logs/verifier/reward.txt" 2>/dev/null || true
cp "$LOGDIR/reward.json" "/logs/verifier/reward.json" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
