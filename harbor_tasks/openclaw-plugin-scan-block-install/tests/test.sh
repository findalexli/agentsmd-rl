#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print(${SCORE} + ${1})"); TOTAL=$(python3 -c "print(${TOTAL} + ${1})"); echo "PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print(${TOTAL} + ${1})"); echo "FAIL ($1): $2"; }

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): Modified files must be parseable TypeScript
for f in src/plugins/install.ts src/plugins/install-security-scan.runtime.ts src/plugins/install-security-scan.ts; do
  if ! node -e "
    const fs = require('fs');
    const ts = require('typescript');
    const code = fs.readFileSync('${REPO}/${f}', 'utf8');
    const result = ts.transpileModule(code, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ESNext } });
    if (!result.outputText) process.exit(1);
  " 2>/dev/null; then
    echo "GATE FAIL: ${f} has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
  fi
done
echo "GATE PASS: TypeScript syntax OK"

# ── Behavioral: Upstream fail-to-pass vitest tests ──────────────────
cd "$REPO"
VITEST_RESULT=0
npx vitest run src/plugins/install.test.ts --reporter=verbose 2>&1 | tee /tmp/vitest_output.txt || VITEST_RESULT=$?

# [pr_diff] (0.20): Package install blocked on dangerous code patterns
if grep -qE '(✓|PASS).*blocks package installs|blocks package installs.*(✓|PASS)' /tmp/vitest_output.txt 2>/dev/null || \
   ([ "$VITEST_RESULT" -eq 0 ] && grep -q "blocks package installs" /tmp/vitest_output.txt 2>/dev/null); then
  pass 0.20 "Package install blocked on dangerous code patterns"
else
  fail 0.20 "Package install NOT blocked on dangerous code patterns"
fi

# [pr_diff] (0.15): Bundle install blocked on dangerous code patterns
if grep -qE '(✓|PASS).*blocks bundle installs|blocks bundle installs.*(✓|PASS)' /tmp/vitest_output.txt 2>/dev/null || \
   ([ "$VITEST_RESULT" -eq 0 ] && grep -q "blocks bundle installs" /tmp/vitest_output.txt 2>/dev/null); then
  pass 0.15 "Bundle install blocked on dangerous code patterns"
else
  fail 0.15 "Bundle install NOT blocked on dangerous code patterns"
fi

# [pr_diff] (0.15): Install blocked when scanner throws
if grep -qE '(✓|PASS).*blocks install when scanner throws|blocks install when scanner throws.*(✓|PASS)' /tmp/vitest_output.txt 2>/dev/null || \
   ([ "$VITEST_RESULT" -eq 0 ] && grep -q "blocks install when scanner throws" /tmp/vitest_output.txt 2>/dev/null); then
  pass 0.15 "Install blocked when scanner throws"
else
  fail 0.15 "Install NOT blocked when scanner throws"
fi

# [pr_diff] (0.15): File install blocked on dangerous code patterns
if grep -qE '(✓|PASS).*blocks plain file installs|blocks plain file installs.*(✓|PASS)' /tmp/vitest_output.txt 2>/dev/null || \
   ([ "$VITEST_RESULT" -eq 0 ] && grep -q "blocks plain file installs" /tmp/vitest_output.txt 2>/dev/null); then
  pass 0.15 "File install blocked on dangerous code patterns"
else
  fail 0.15 "File install NOT blocked on dangerous code patterns"
fi

# ── Behavioral: error codes are machine-readable ────────────────────
# [pr_diff] (0.10): Install error code object has at least 2 scan/security-related entries
# Uses TS AST — accepts any naming convention, not just the gold patch names
node -e "
  const fs = require('fs');
  const ts = require('typescript');
  const code = fs.readFileSync('${REPO}/src/plugins/install.ts', 'utf8');
  const sf = ts.createSourceFile('install.ts', code, ts.ScriptTarget.Latest, true);
  let scanCodeCount = 0;
  function visit(node) {
    if (ts.isPropertyAssignment(node)) {
      const name = (node.name.getText(sf) || '').toLowerCase();
      const init = node.initializer && ts.isStringLiteral(node.initializer)
        ? node.initializer.text.toLowerCase() : '';
      if ((name.includes('scan') || name.includes('security')) &&
          (init.includes('scan') || init.includes('security') || init.includes('block'))) {
        scanCodeCount++;
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (scanCodeCount < 2) process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
  pass 0.10 "Install error code object has scan-related error codes"
else
  fail 0.10 "Missing scan-related error codes in install error code object"
fi

# ── Behavioral: scan result type supports block code ────────────────
# [agent_config] (0.05): "Prefer Result<T, E>-style outcomes and closed error-code unions" — CLAUDE.md:150
# The blocked type must have a field beyond just 'reason' for machine-readable distinction
node -e "
  const fs = require('fs');
  const code1 = fs.readFileSync('${REPO}/src/plugins/install-security-scan.runtime.ts', 'utf8');
  const code2 = fs.readFileSync('${REPO}/src/plugins/install-security-scan.ts', 'utf8');
  const combined = code1 + code2;
  const blockedMatch = combined.match(/blocked\\??:\\s*\\{([^}]+)\\}/s);
  if (!blockedMatch) process.exit(1);
  const fields = blockedMatch[1];
  if (!fields.includes('reason')) process.exit(1);
  const fieldCount = (fields.match(/\\w+\\??\\s*:/g) || []).length;
  if (fieldCount < 2) process.exit(1);
" 2>/dev/null
if [ $? -eq 0 ]; then
  pass 0.05 "Scan result blocked type has structured code field"
else
  fail 0.05 "Scan result blocked type missing structured code field"
fi

# ── Pass-to-pass: upstream test suite passes fully ──────────────────
# [pr_diff] (0.10): Overall vitest suite passes including non-blocking scenarios
if [ "$VITEST_RESULT" -eq 0 ]; then
  pass 0.10 "All upstream install tests pass (including non-blocking scenarios)"
else
  # Partial credit if most tests pass
  PASS_COUNT=$(grep -cE '✓|PASS' /tmp/vitest_output.txt 2>/dev/null || echo 0)
  FAIL_COUNT=$(grep -cE '✗|×|FAIL' /tmp/vitest_output.txt 2>/dev/null || echo 0)
  if [ "$PASS_COUNT" -gt 4 ] && [ "$FAIL_COUNT" -le 1 ]; then
    pass 0.05 "Most upstream install tests pass (minor failures)"
  else
    fail 0.10 "Upstream install tests have significant failures"
  fi
fi

# ── Finalize ────────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${SCORE} / 1.0 (before LLM rubric)"
echo "${SCORE}" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('${SCORE}')
json.dump({
    'reward': score,
    'behavioral': min(score, 0.75),
    'regression': min(max(score - 0.75, 0), 0.10),
    'config': min(max(score - 0.85, 0), 0.05),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(json.load(open('/logs/verifier/reward.json')), indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
