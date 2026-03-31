#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=100
REPO="/workspace/openclaw"
TARGET_FILE="$REPO/src/security/audit.test.ts"

# Helper: strip ANSI escape codes
strip_ansi() { sed 's/\x1b\[[0-9;]*m//g'; }

echo "=== openclaw-config-audit-exec-override grading ==="

# ─────────────────────────────────────────────────────────
# GATE (0.00): TypeScript syntax check — abort on failure
# ─────────────────────────────────────────────────────────
echo "[GATE] TypeScript syntax check on modified file..."
if [[ ! -f "$TARGET_FILE" ]]; then
  echo "  FAIL: audit.test.ts not found"
  echo "0.0" > /logs/verifier/reward.txt
  echo "0.0" > "/logs/verifier/reward.txt" 2>/dev/null || true
  exit 0
fi

if ! node -e "
  const fs = require('fs');
  const code = fs.readFileSync('$TARGET_FILE', 'utf8');
  try {
    require('esbuild').transformSync(code, { loader: 'ts' });
    process.exit(0);
  } catch(e) {
    console.error(e.message);
    process.exit(1);
  }
" 2>/dev/null; then
  echo "  GATE FAILED: audit.test.ts has syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo "0.0" > "/logs/verifier/reward.txt" 2>/dev/null || true
  exit 0
fi
echo "  GATE: PASS"

# ─────────────────────────────────────────────────────────
# F2P BEHAVIORAL (0.25): Verify exec test case exists and vitest passes
# The new test case is added inside runConfigAuditCases, so individual
# cases don't appear as separate lines in vitest verbose output. Instead:
#   1. Check that the test file now has exec in a tools.allow config
#   2. Check that the overall audit test suite passes
# ─────────────────────────────────────────────────────────
# [pr_diff] (0.25): exec test case added and audit test suite passes
echo "[F2P] Running vitest on audit test file..."
cd "$REPO"
VITEST_OUTPUT=$(timeout 90 npx vitest run src/security/audit.test.ts --reporter=verbose 2>&1 | strip_ansi || true)
cd /

F2P_VITEST=0
# Check: test file has exec in a tools.allow config (not just a comment)
HAS_EXEC_ALLOW=$(node -e "
  const fs = require('fs');
  const code = fs.readFileSync('$TARGET_FILE', 'utf8');
  const noComments = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  const hasExecInConfig = /tools\s*:\s*\{[^}]*allow\s*:\s*\[[^\]]*['\"]exec['\"]/s.test(noComments);
  console.log(hasExecInConfig ? 'true' : 'false');
" 2>/dev/null || echo "false")

# Check: vitest passed overall (all tests)
VITEST_ALL_PASS=$(echo "$VITEST_OUTPUT" | grep -P 'Tests\s+\d+ passed' | head -1)
VITEST_ANY_FAIL=$(echo "$VITEST_OUTPUT" | grep -oP '(\d+) failed' | head -1 | grep -oP '\d+' || echo "0")

if [[ "$HAS_EXEC_ALLOW" == "true" && -n "$VITEST_ALL_PASS" && "$VITEST_ANY_FAIL" == "0" ]]; then
  echo "  PASS: exec test case in tools.allow config and all vitest tests pass"
  F2P_VITEST=25
elif [[ "$HAS_EXEC_ALLOW" == "true" && -n "$VITEST_ALL_PASS" ]]; then
  echo "  PARTIAL: exec config found but some tests failed ($VITEST_ANY_FAIL failures)"
  F2P_VITEST=15
elif [[ "$HAS_EXEC_ALLOW" == "true" ]]; then
  echo "  PARTIAL: exec config found but vitest did not confirm all pass"
  F2P_VITEST=10
else
  echo "  FAIL: No exec test case in tools.allow config"
fi
SCORE=$((SCORE + F2P_VITEST))

# ─────────────────────────────────────────────────────────
# F2P BEHAVIORAL (0.40): Mutation test — proves test is real
# Rename 'exec' → 'exec_MUTANT' in dangerous-tools.ts so the audit
# no longer treats exec as dangerous. If the agent's test is real,
# it should now FAIL (the audit won't flag exec in tools.allow).
# A stub test like expect(true).toBe(true) won't detect this.
# ─────────────────────────────────────────────────────────
# [pr_diff] (0.40): Mutation test — exec removed from deny list causes test failure
echo "[F2P] Mutation test: removing exec from deny list..."
F2P_MUTATION=0
cd "$REPO"

# Save original
DENY_FILE=$(find src/security -name 'dangerous*' -o -name 'deny*' -o -name 'blocked*' 2>/dev/null | head -1)
if [[ -z "$DENY_FILE" ]]; then
  DENY_FILE=$(grep -rl "'exec'" src/security/ 2>/dev/null | grep -v test | grep -v '.bak' | head -1)
fi

if [[ -n "$DENY_FILE" && -f "$DENY_FILE" ]]; then
  cp "$DENY_FILE" "${DENY_FILE}.bak"

  # Mutate: rename 'exec' to 'exec_MUTANT' so it's no longer matched
  node -e "
    const fs = require('fs');
    let code = fs.readFileSync('$DENY_FILE', 'utf8');
    code = code.replace(/['\"]exec['\"]/g, '\"exec_MUTANT\"');
    fs.writeFileSync('$DENY_FILE', code);
  " 2>/dev/null

  echo "  Running vitest with mutated deny list..."
  MUTANT_OUTPUT=$(timeout 90 npx vitest run src/security/audit.test.ts --reporter=verbose 2>&1 | strip_ansi || true)

  # Restore original
  mv "${DENY_FILE}.bak" "$DENY_FILE" 2>/dev/null

  # Check: did any tests FAIL under mutation?
  MUTANT_FAIL_COUNT=$(echo "$MUTANT_OUTPUT" | grep -oP '(\d+) failed' | head -1 | grep -oP '\d+' || echo "0")
  MUTANT_EXEC_FAIL=$(echo "$MUTANT_OUTPUT" | grep -iP '(✗|×|FAIL).*exec|exec.*(✗|×|FAIL)' | head -1)
  # Also check for failed test related to gateway.tools.allow (the describe block name)
  MUTANT_TOOLS_FAIL=$(echo "$MUTANT_OUTPUT" | grep -iP '(✗|×|FAIL).*(tools\.allow|dangerous.*gateway)' | head -1)

  if [[ -n "$MUTANT_EXEC_FAIL" ]]; then
    echo "  PASS: Mutation caught — agent's test correctly detects exec removal"
    echo "  Line: $MUTANT_EXEC_FAIL"
    F2P_MUTATION=40
  elif [[ -n "$MUTANT_TOOLS_FAIL" ]]; then
    echo "  PASS: Mutation caught — gateway.tools.allow test failed under mutation"
    echo "  Line: $MUTANT_TOOLS_FAIL"
    F2P_MUTATION=40
  elif [[ "$MUTANT_FAIL_COUNT" -gt 0 ]]; then
    echo "  PARTIAL: $MUTANT_FAIL_COUNT tests failed under mutation (likely exec-related)"
    F2P_MUTATION=25
  else
    echo "  FAIL: Tests still pass with exec removed — test is a stub or trivial"
  fi
else
  echo "  SKIP: Could not find dangerous tools file for mutation"
  if [[ "$F2P_VITEST" -gt 0 ]]; then
    F2P_MUTATION=10
    echo "  PARTIAL: Vitest passed but mutation not possible"
  fi
fi
cd /
SCORE=$((SCORE + F2P_MUTATION))

# ─────────────────────────────────────────────────────────
# P2P REGRESSION (0.15): All existing audit tests still pass
# ─────────────────────────────────────────────────────────
# [pr_diff] (0.15): Existing audit tests still pass after agent's changes
echo "[P2P] Checking all existing audit tests still pass..."
P2P_SCORE=0
if echo "$VITEST_OUTPUT" | grep -qP 'Tests\s+\d+ passed'; then
  if [[ "$VITEST_ANY_FAIL" == "0" ]]; then
    echo "  PASS: All existing audit tests pass"
    P2P_SCORE=15
  else
    echo "  FAIL: $VITEST_ANY_FAIL tests failed"
    PASSED_COUNT=$(echo "$VITEST_OUTPUT" | grep -oP '(\d+) passed' | head -1 | grep -oP '\d+' || echo "0")
    if [[ "$PASSED_COUNT" -gt "$VITEST_ANY_FAIL" ]]; then
      P2P_SCORE=8
      echo "  PARTIAL: Most tests pass ($PASSED_COUNT passed, $VITEST_ANY_FAIL failed)"
    fi
  fi
else
  echo "  FAIL: Could not confirm test suite passed"
fi
SCORE=$((SCORE + P2P_SCORE))

# ─────────────────────────────────────────────────────────
# STRUCTURAL / ANTI-STUB (0.10)
# ─────────────────────────────────────────────────────────

# [pr_diff] (0.05): Test file has exec in a tools.allow config object (not just a comment)
echo "[STRUCT] Checking test has exec in tools.allow config..."
STRUCT_CONFIG=0
if [[ "$HAS_EXEC_ALLOW" == "true" ]]; then
  echo "  PASS: Test has exec in tools.allow config object"
  STRUCT_CONFIG=5
else
  echo "  FAIL: No exec in tools.allow config found (excluding comments)"
fi
SCORE=$((SCORE + STRUCT_CONFIG))

# [pr_diff] (0.05): Test has critical severity assertion for exec case
echo "[STRUCT] Checking for critical severity assertion..."
STRUCT_SEVERITY=0
HAS_CRITICAL=$(node -e "
  const fs = require('fs');
  const code = fs.readFileSync('$TARGET_FILE', 'utf8');
  const noComments = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
  // Find exec mentions and check for critical severity nearby
  const parts = noComments.split(/['\"]exec['\"]/);
  if (parts.length < 2) { console.log('false'); process.exit(0); }
  // Check 500 chars before and after each exec mention
  for (let i = 1; i < parts.length; i++) {
    const before = parts[i-1].slice(-500);
    const after = parts[i].slice(0, 500);
    const region = before + after;
    if (/expectedSeverity.*['\"]critical['\"]|severity.*['\"]critical['\"]|critical/i.test(region)) {
      console.log('true');
      process.exit(0);
    }
  }
  console.log('false');
" 2>/dev/null || echo "false")

if [[ "$HAS_CRITICAL" == "true" ]]; then
  echo "  PASS: Critical severity assertion found near exec config"
  STRUCT_SEVERITY=5
else
  echo "  FAIL: No critical severity assertion found near exec"
fi
SCORE=$((SCORE + STRUCT_SEVERITY))

# ─────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10)
# ─────────────────────────────────────────────────────────

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144 @ 1ca4261
echo "[CONFIG] Checking strict typing..."
CONFIG_TYPING=0
EXEC_REGION=$(grep -A5 -B5 "exec" "$TARGET_FILE" 2>/dev/null | grep -c ": any\|as any" || true)
EXEC_REGION=${EXEC_REGION:-0}
if [[ "$EXEC_REGION" -le 2 ]]; then
  echo "  PASS: No excessive any types near exec test code"
  CONFIG_TYPING=5
else
  echo "  FAIL: Too many any types near exec test code ($EXEC_REGION)"
fi
SCORE=$((SCORE + CONFIG_TYPING))

# [agent_config] (0.05): "Written English: use American spelling" — CLAUDE.md:167 @ 1ca4261
echo "[CONFIG] Checking American English..."
CONFIG_SPELLING=0
BRITISH=$(grep -ciP 'colour|behaviour|organise|analyse|authorise|minimise' "$TARGET_FILE" 2>/dev/null || true)
BRITISH=${BRITISH:-0}
if [[ "$BRITISH" -le 0 ]] 2>/dev/null; then
  echo "  PASS: American English used"
  CONFIG_SPELLING=5
else
  echo "  FAIL: British spelling found ($BRITISH occurrences)"
fi
SCORE=$((SCORE + CONFIG_SPELLING))

# ─────────────────────────────────────────────────────────
# FINAL SCORE
# ─────────────────────────────────────────────────────────

FINAL=$(python3 -c "print(f'{$SCORE / $TOTAL:.4f}')" 2>/dev/null || echo "0.0")
echo ""
echo "=== FINAL SCORE: $SCORE / $TOTAL = $FINAL ==="

echo "$FINAL" > /logs/verifier/reward.txt
echo "$FINAL" > "/logs/verifier/reward.txt" 2>/dev/null || true

python3 -c "
import json
score = $SCORE / $TOTAL
reward = {
    'reward': round(score, 4),
    'behavioral': round(($F2P_VITEST + $F2P_MUTATION) / $TOTAL, 4),
    'regression': round($P2P_SCORE / $TOTAL, 4),
    'structural': round(($STRUCT_CONFIG + $STRUCT_SEVERITY) / $TOTAL, 4),
    'config': round(($CONFIG_TYPING + $CONFIG_SPELLING) / $TOTAL, 4),
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(reward, f, indent=2)
print(json.dumps(reward, indent=2))
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
