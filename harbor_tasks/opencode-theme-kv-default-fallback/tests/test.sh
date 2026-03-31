#!/usr/bin/env bash
set -uo pipefail

FILE="packages/opencode/src/cli/cmd/tui/context/theme.tsx"

########################################
# GATE: File exists and is non-empty
########################################
# [static] (gate): File must exist and be non-empty
if [ ! -s "$FILE" ]; then
  echo "GATE FAIL: $FILE does not exist or is empty"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
  exit 0
fi

echo "GATE: passed"

########################################
# Node.js analysis: comment-stripped checks on memo block
########################################
# WHY NOT CALLABLE: createMemo requires full SolidJS reactive runtime + useKV/useRenderer
# providers + @opentui/core RGBA class — none installable without full monorepo build.
# Instead we strip comments and analyze the code structure to prevent gaming via comments.

cat > /tmp/analyze_memo.js <<'ANALYZE_EOF'
const fs = require("fs");
const file = process.argv[2];
const src = fs.readFileSync(file, "utf8");

// Strip single-line and multi-line comments
const stripped = src.replace(/\/\/[^\n]*/g, "").replace(/\/\*[\s\S]*?\*\//g, "");

// Find the createMemo block for 'values' using brace counting
const memoIdx = stripped.indexOf("const values = createMemo");
let memo = "";
if (memoIdx !== -1) {
  const braceStart = stripped.indexOf("{", memoIdx);
  if (braceStart !== -1) {
    let depth = 1;
    let i = braceStart + 1;
    while (i < stripped.length && depth > 0) {
      if (stripped[i] === "{") depth++;
      if (stripped[i] === "}") depth--;
      i++;
    }
    memo = stripped.substring(braceStart + 1, i - 1);
  }
}

const results = {};
results.memoFound = memo.length > 10;

// Check 1: kv.get("theme") appears in actual code (not comments)
results.kvGet = /kv\.get\s*\(\s*["'`]theme["'`]\s*\)/.test(memo);

// Check 2: Buggy single-expression pattern is gone
// Bug: resolveTheme(store.themes[store.active] ?? store.themes.opencode, ...)
// Also catch bracket notation: store.themes["opencode"]
results.buggyPatternGone = !/store\.themes\[store\.active\]\s*(\?\?|\|\|)\s*store\.themes[.\[]/.test(memo);

// Check 3: KV result feeds into store.themes lookup
// The kv.get result must be used to index store.themes (not just called and ignored)
results.kvFeedsLookup =
  /kv\.get\s*\([^)]*\)[\s\S]*?store\.themes\[/.test(memo) ||
  /store\.themes\[.*kv\.get/.test(memo);

// Check 4: Multiple code paths (branching for fallback chain)
const resolveCount = (memo.match(/resolveTheme\s*\(/g) || []).length;
const hasConditional = /\bif\s*\(/.test(memo);
results.multipleCodePaths = resolveCount >= 2 || hasConditional;

console.log(JSON.stringify(results));
ANALYZE_EOF

ANALYSIS=$(node /tmp/analyze_memo.js "$FILE" 2>/dev/null)

if [ -z "$ANALYSIS" ]; then
  echo "WARN: Node.js analysis failed"
  ANALYSIS='{"memoFound":false,"kvGet":false,"buggyPatternGone":false,"kvFeedsLookup":false,"multipleCodePaths":false}'
fi

echo "Analysis: $ANALYSIS"

# Helper to extract a boolean field from the JSON
jval() { node -e "process.stdout.write(String(JSON.parse(process.argv[1])['$1']))" "$ANALYSIS"; }

# If memo block wasn't found at all, gate-fail
if [ "$(jval memoFound)" != "true" ]; then
  echo "GATE FAIL: createMemo 'values' block not found or too small"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
  exit 0
fi

BEHAVIORAL=0

# [pr_diff] (0.30): kv.get("theme") present in memo code (comment-stripped)
if [ "$(jval kvGet)" = "true" ]; then
  echo "PASS (0.30): kv.get('theme') found in memo code (comment-stripped)"
  BEHAVIORAL=$(echo "$BEHAVIORAL + 0.30" | bc)
else
  echo "FAIL (0.30): kv.get('theme') NOT found in memo code"
fi

# [pr_diff] (0.20): Buggy single-expression nullish-coalescing fallback removed
if [ "$(jval buggyPatternGone)" = "true" ]; then
  echo "PASS (0.20): Buggy direct-fallback pattern removed"
  BEHAVIORAL=$(echo "$BEHAVIORAL + 0.20" | bc)
else
  echo "FAIL (0.20): Buggy store.themes[store.active] ?? store.themes.opencode still present"
fi

# [pr_diff] (0.15): KV result used to look up theme in store.themes
if [ "$(jval kvFeedsLookup)" = "true" ]; then
  echo "PASS (0.15): KV result feeds into store.themes lookup"
  BEHAVIORAL=$(echo "$BEHAVIORAL + 0.15" | bc)
else
  echo "FAIL (0.15): KV result not used for theme lookup"
fi

# [pr_diff] (0.05): Multiple code paths or conditional branching in memo
if [ "$(jval multipleCodePaths)" = "true" ]; then
  echo "PASS (0.05): Multiple code paths / conditional logic in memo"
  BEHAVIORAL=$(echo "$BEHAVIORAL + 0.05" | bc)
else
  echo "FAIL (0.05): Single code path — no fallback branching detected"
fi

echo "behavioral subtotal: $BEHAVIORAL"

########################################
# PASS-TO-PASS: Exports preserved
########################################
REGRESSION=0

# [repo_tests] (0.05): resolveTheme function must still be exported
if grep -q 'export function resolveTheme' "$FILE"; then
  echo "PASS (0.05): resolveTheme export preserved"
  REGRESSION=$(echo "$REGRESSION + 0.05" | bc)
else
  echo "FAIL (0.05): resolveTheme export missing"
fi

# [repo_tests] (0.05): useTheme and ThemeProvider must still be exported
if grep -qE 'use:\s*useTheme.*provider:\s*ThemeProvider|provider:\s*ThemeProvider.*use:\s*useTheme' "$FILE"; then
  echo "PASS (0.05): useTheme/ThemeProvider exports preserved"
  REGRESSION=$(echo "$REGRESSION + 0.05" | bc)
else
  echo "FAIL (0.05): useTheme/ThemeProvider exports missing"
fi

# [repo_tests] (0.05): DEFAULT_THEMES record must still be exported
if grep -q 'export const DEFAULT_THEMES' "$FILE"; then
  echo "PASS (0.05): DEFAULT_THEMES export preserved"
  REGRESSION=$(echo "$REGRESSION + 0.05" | bc)
else
  echo "FAIL (0.05): DEFAULT_THEMES export missing"
fi

echo "regression subtotal: $REGRESSION"

########################################
# STRUCTURAL: Anti-stub check
########################################
# [static] (0.05): File must not be stubbed out
STRUCTURAL=0
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -ge 200 ]; then
  echo "PASS (0.05): File has $LINE_COUNT lines (not stubbed)"
  STRUCTURAL=0.05
else
  echo "FAIL (0.05): File only has $LINE_COUNT lines — likely stubbed"
fi

echo "structural subtotal: $STRUCTURAL"

########################################
# CONFIG-DERIVED
########################################
CONFIG=0

# Extract memo block (raw, for config style checks)
MEMO_BLOCK=$(sed -n '/const values = createMemo/,/^[[:space:]]*})/p' "$FILE")

# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:13 @ 26382c6
if echo "$MEMO_BLOCK" | grep -qE ':\s*any\b|as\s+any\b|<any>'; then
  echo "FAIL (0.05): 'any' type found in values memo"
else
  echo "PASS (0.05): No 'any' type in values memo"
  CONFIG=$(echo "$CONFIG + 0.05" | bc)
fi

# [agent_config] (0.05): "Avoid try/catch where possible" — AGENTS.md:12 @ 26382c6
if echo "$MEMO_BLOCK" | grep -qE '\btry\s*\{'; then
  echo "FAIL (0.05): try/catch found in values memo"
else
  echo "PASS (0.05): No try/catch in values memo"
  CONFIG=$(echo "$CONFIG + 0.05" | bc)
fi

echo "config subtotal: $CONFIG"

########################################
# Compute total
########################################
REWARD=$(echo "$BEHAVIORAL + $REGRESSION + $STRUCTURAL + $CONFIG" | bc)
echo ""
echo "=== REWARD BREAKDOWN ==="
echo "behavioral:  $BEHAVIORAL"
echo "regression:  $REGRESSION"
echo "structural:  $STRUCTURAL"
echo "config:      $CONFIG"
echo "TOTAL:       $REWARD"

echo "$REWARD" > /logs/verifier/reward.txt
cat > /logs/verifier/reward.json <<SCORES
{"reward":$REWARD,"behavioral":$BEHAVIORAL,"regression":$REGRESSION,"config":$CONFIG,"style_rubric":0}
SCORES

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
