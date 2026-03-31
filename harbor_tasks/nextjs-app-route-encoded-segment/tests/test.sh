#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0
GATE_PASS=true

cd /workspace/next.js

##############################################################################
# GATE: Syntax check on modified file
##############################################################################
# [pr_diff] (gate): Modified TypeScript file must parse without syntax errors
tsx --eval "
import './packages/next/src/shared/lib/router/routes/app.ts'
console.log('OK')
" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "GATE FAIL: packages/next/src/shared/lib/router/routes/app.ts has import errors"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: TypeScript import check passed"

##############################################################################
# Write behavioral test file
##############################################################################
cat > /tmp/test_encoded_segment.ts <<'TESTEOF'
import { parseAppRoute } from './packages/next/src/shared/lib/router/routes/app.js'

const results: Record<string, boolean> = {}

// Test 1: encoded single dynamic placeholder recognized
try {
  const route = parseAppRoute('/vercel/%5BprojectSlug%5D', false)
  const names = route.dynamicSegments.map((s: any) => s.param.paramName)
  results['encoded_single'] = names.includes('projectSlug')
} catch {
  results['encoded_single'] = false
}

// Test 2: multiple encoded placeholders in same path
try {
  const route = parseAppRoute('/%5BteamSlug%5D/project/%5BprojectSlug%5D', false)
  const names = route.dynamicSegments.map((s: any) => s.param.paramName)
  results['encoded_multi'] = names.includes('teamSlug') && names.includes('projectSlug')
} catch {
  results['encoded_multi'] = false
}

// Test 3: mixed encoded and non-encoded segments
try {
  const route = parseAppRoute('/[teamSlug]/%5BprojectSlug%5D', false)
  const names = route.dynamicSegments.map((s: any) => s.param.paramName)
  results['encoded_mixed'] = names.includes('teamSlug') && names.includes('projectSlug')
} catch {
  results['encoded_mixed'] = false
}

// Test 4: encoded catchall segment
try {
  const route = parseAppRoute('/%5B...slug%5D', false)
  const names = route.dynamicSegments.map((s: any) => s.param.paramName)
  results['encoded_catchall'] = names.includes('slug')
} catch {
  results['encoded_catchall'] = false
}

// Test 5: malformed encoding does not crash
try {
  parseAppRoute('/test/%5Bparam', false)
  results['malformed_no_crash'] = true
} catch {
  results['malformed_no_crash'] = false
}

// Test 6 (P2P): normal non-encoded dynamic segments still work
try {
  const route = parseAppRoute('/blog/[slug]/[id]', false)
  const names = route.dynamicSegments.map((s: any) => s.param.paramName)
  results['normal_dynamic'] = names.includes('slug') && names.includes('id')
} catch {
  results['normal_dynamic'] = false
}

// Test 7 (P2P): static segments still parsed correctly
try {
  const route = parseAppRoute('/about/contact', false)
  results['static_segments'] = route.dynamicSegments.length === 0 &&
    route.segments.some((s: any) => s.type === 'static' && s.name === 'about') &&
    route.segments.some((s: any) => s.type === 'static' && s.name === 'contact')
} catch {
  results['static_segments'] = false
}

// Test 8 (P2P): non-encoded segment that looks like encoding but isn't
try {
  const route = parseAppRoute('/foo/bar', false)
  results['plain_static'] = route.dynamicSegments.length === 0
} catch {
  results['plain_static'] = false
}

// Output results as JSON
console.log(JSON.stringify(results))
TESTEOF

##############################################################################
# Run behavioral tests
##############################################################################
TEST_OUTPUT=$(cd /workspace/next.js && tsx /tmp/test_encoded_segment.ts 2>/dev/null || echo '{}')
echo "Test output: $TEST_OUTPUT"

get_result() {
    echo "$TEST_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('true' if d.get('$1') else 'false')" 2>/dev/null || echo "false"
}

##############################################################################
# Fail-to-pass: Behavioral tests (0.65 total)
##############################################################################

# [pr_diff] (0.25): Encoded single dynamic placeholder %5BprojectSlug%5D is recognized
RESULT=$(get_result "encoded_single")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.25" | bc)
    echo "PASS [0.25]: encoded single dynamic placeholder recognized"
else
    echo "FAIL [0.25]: encoded single dynamic placeholder not recognized"
fi
TOTAL=$(echo "$TOTAL + 0.25" | bc)

# [pr_diff] (0.15): Multiple encoded placeholders in same path both recognized
RESULT=$(get_result "encoded_multi")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.15" | bc)
    echo "PASS [0.15]: multiple encoded placeholders recognized"
else
    echo "FAIL [0.15]: multiple encoded placeholders not recognized"
fi
TOTAL=$(echo "$TOTAL + 0.15" | bc)

# [pr_diff] (0.10): Mixed encoded and non-encoded segments handled
RESULT=$(get_result "encoded_mixed")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.10" | bc)
    echo "PASS [0.10]: mixed encoded/non-encoded segments handled"
else
    echo "FAIL [0.10]: mixed encoded/non-encoded segments not handled"
fi
TOTAL=$(echo "$TOTAL + 0.10" | bc)

# [pr_diff] (0.10): Encoded catchall segment recognized
RESULT=$(get_result "encoded_catchall")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.10" | bc)
    echo "PASS [0.10]: encoded catchall segment recognized"
else
    echo "FAIL [0.10]: encoded catchall segment not recognized"
fi
TOTAL=$(echo "$TOTAL + 0.10" | bc)

# [pr_diff] (0.05): Malformed URL encoding does not crash
RESULT=$(get_result "malformed_no_crash")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: malformed encoding does not crash"
else
    echo "FAIL [0.05]: malformed encoding caused a crash"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Pass-to-pass: Regression checks (0.15 total)
##############################################################################

# [pr_diff] (0.05): Non-encoded dynamic segments still work
RESULT=$(get_result "normal_dynamic")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: non-encoded dynamic segments still work"
else
    echo "FAIL [0.05]: non-encoded dynamic segments broken"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Static segments still parsed correctly
RESULT=$(get_result "static_segments")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: static segments still work"
else
    echo "FAIL [0.05]: static segments broken"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Plain paths without encoding still work
RESULT=$(get_result "plain_static")
if [ "$RESULT" = "true" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: plain static paths still work"
else
    echo "FAIL [0.05]: plain static paths broken"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Structural: Anti-stub checks (0.10 total)
##############################################################################

# [pr_diff] (0.05): The source file was actually modified (not a no-op)
if ! git diff --quiet packages/next/src/shared/lib/router/routes/app.ts 2>/dev/null; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: app.ts was modified"
else
    echo "FAIL [0.05]: app.ts was not modified"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Fix handles URL decoding (decodeURIComponent or equivalent)
if grep -qE 'decodeURIComponent|decodeURI|unescape|%5[bB]|%5[dD]' packages/next/src/shared/lib/router/routes/app.ts 2>/dev/null; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: URL decoding logic present in app.ts"
else
    echo "FAIL [0.05]: no URL decoding logic found in app.ts"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): No hardcoded secret values — AGENTS.md:284-290 @ 56d75a0
# "Never print or paste secret values (tokens, API keys, cookies)"
if grep -iE '(api[_-]?key|secret|token|password|credential)\s*[:=]\s*["\x27]' packages/next/src/shared/lib/router/routes/app.ts 2>/dev/null; then
    echo "FAIL [0.05]: hardcoded secret values found"
else
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: no hardcoded secret values"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [agent_config] (0.05): No console.log debug output left in production code — AGENTS.md general practice
if git diff packages/next/src/shared/lib/router/routes/app.ts 2>/dev/null | grep -E '^\+.*console\.(log|debug|warn)' | grep -v '^\+\+\+' >/dev/null 2>&1; then
    echo "FAIL [0.05]: console.log debug output left in production code"
else
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: no debug console.log in production code"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS" | bc)
echo ""
echo "Total: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt

echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
