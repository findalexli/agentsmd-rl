#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

REPO="/workspace/openclaw"
EVAL_SRC="$REPO/src/infra/exec-inline-eval.ts"
ALLOWLIST_SRC="$REPO/src/infra/exec-approvals-allowlist.ts"

# ========== GATE: Syntax check ==========
# [pr_diff] (0): TypeScript files must parse without syntax errors

GATE_PASS=1
for f in "$EVAL_SRC" "$ALLOWLIST_SRC"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=0
        continue
    fi
    node -e "
      const fs = require('fs');
      const src = fs.readFileSync('$f', 'utf8');
      let depth = 0;
      for (const ch of src) {
        if (ch === '{') depth++;
        else if (ch === '}') depth--;
      }
      if (depth !== 0) process.exit(1);
    " 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: $f has unbalanced braces"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    echo "GATE FAILED: syntax errors"
    exit 0
fi

# ========== BEHAVIORAL TESTS (tsx) ==========
# Write a test script that imports and calls the actual functions

cat > "$REPO/__behavioral_test.mts" << 'TESTEOF'
import { isInterpreterLikeAllowlistPattern, detectInterpreterInlineEvalArgv } from "./src/infra/exec-inline-eval.js";

interface TestResult {
  name: string;
  pass: boolean;
  error?: string;
}

const results: TestResult[] = [];

function test(name: string, fn: () => void) {
  try {
    fn();
    results.push({ name, pass: true });
  } catch (e: unknown) {
    results.push({ name, pass: false, error: e instanceof Error ? e.message : String(e) });
  }
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

// ===== FAIL-TO-PASS: isInterpreterLikeAllowlistPattern for awk family =====

test("f2p_allowlist_awk", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/awk") === true,
    "expected /usr/bin/awk to be interpreter-like");
});

test("f2p_allowlist_gawk_mawk_nawk", () => {
  assert(isInterpreterLikeAllowlistPattern("**/gawk") === true, "gawk should be interpreter-like");
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/mawk") === true, "mawk should be interpreter-like");
  assert(isInterpreterLikeAllowlistPattern("nawk") === true, "nawk should be interpreter-like");
});

// ===== FAIL-TO-PASS: detectInterpreterInlineEvalArgv for awk inline programs =====

test("f2p_detect_awk_positional", () => {
  const hit = detectInterpreterInlineEvalArgv(["awk", "{print $1}", "data.csv"]);
  assert(hit !== null && hit !== undefined, "expected awk inline program to be detected");
});

test("f2p_detect_gawk_with_F_flag", () => {
  const hit = detectInterpreterInlineEvalArgv(["gawk", "-F", ",", "{print $1}", "data.csv"]);
  assert(hit !== null && hit !== undefined, "expected gawk inline program to be detected after -F flag");
});

// ===== PASS-TO-PASS: Existing interpreters still work =====

test("p2p_python_allowlist", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/python3") === true,
    "python3 should still be interpreter-like");
});

test("p2p_python_inline_eval", () => {
  const hit = detectInterpreterInlineEvalArgv(["python3", "-c", "print(1)"]);
  assert(hit !== null && hit !== undefined, "python3 -c should still be detected");
});

test("p2p_awk_file_not_inline", () => {
  const hit = detectInterpreterInlineEvalArgv(["awk", "-f", "script.awk", "data.csv"]);
  assert(hit === null || hit === undefined, "awk -f should NOT be detected as inline eval");
});

// ===== NEGATIVE: Non-interpreter programs must NOT be detected =====

test("neg_allowlist_ls", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/ls") === false,
    "ls should not be interpreter-like");
});

test("neg_allowlist_cat", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/cat") === false,
    "cat should not be interpreter-like");
});

test("neg_allowlist_rg", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/rg") === false,
    "rg should not be interpreter-like");
});

test("neg_allowlist_grep", () => {
  assert(isInterpreterLikeAllowlistPattern("/usr/bin/grep") === false,
    "grep should not be interpreter-like");
});

test("neg_detect_ls", () => {
  const hit = detectInterpreterInlineEvalArgv(["ls", "-la", "/tmp"]);
  assert(hit === null || hit === undefined, "ls should not be detected as inline eval");
});

test("neg_detect_cat", () => {
  const hit = detectInterpreterInlineEvalArgv(["cat", "file.txt"]);
  assert(hit === null || hit === undefined, "cat should not be detected as inline eval");
});

test("neg_detect_grep", () => {
  const hit = detectInterpreterInlineEvalArgv(["grep", "-r", "pattern", "."]);
  assert(hit === null || hit === undefined, "grep should not be detected as inline eval");
});

// Output JSON results
console.log(JSON.stringify(results));
TESTEOF

# Run the behavioral test
BEHAVIORAL_OUTPUT=$(cd "$REPO" && npx tsx __behavioral_test.mts 2>/dev/null)
BEHAVIORAL_EXIT=$?

# Clean up test file
rm -f "$REPO/__behavioral_test.mts"

if [ "$BEHAVIORAL_EXIT" -ne 0 ] || [ -z "$BEHAVIORAL_OUTPUT" ]; then
    echo "WARNING: Behavioral test runner failed (exit=$BEHAVIORAL_EXIT)"
    BEHAVIORAL_OUTPUT="[]"
fi

# Parse behavioral test results
parse_test() {
    local test_name="$1"
    python3 -c "
import json, sys
results = json.loads('''$BEHAVIORAL_OUTPUT''')
for r in results:
    if r['name'] == '$test_name':
        print('1' if r['pass'] else '0')
        sys.exit(0)
print('0')
" 2>/dev/null || echo "0"
}

# Track category scores
F2P_SCORE=0
P2P_SCORE=0
NEG_SCORE=0
STRUCT_SCORE=0
CONFIG_SCORE=0

add_categorized() {
    local weight="$1" pass="$2" tag="$3" desc="$4" cat="$5"
    add_result "$weight" "$pass" "$tag" "$desc"
    if [ "$pass" = "1" ]; then
        eval "${cat}_SCORE=\$(python3 -c \"print(round(\$${cat}_SCORE + $weight, 4))\")"
    fi
}

# ========== FAIL-TO-PASS: Core awk handling (0.475) ==========

# [pr_diff] (0.15): isInterpreterLikeAllowlistPattern recognizes awk executables
PASS=$(parse_test "f2p_allowlist_awk")
add_categorized 0.15 "$PASS" "pr_diff" "isInterpreterLikeAllowlistPattern recognizes /usr/bin/awk" "F2P"

# [pr_diff] (0.10): isInterpreterLikeAllowlistPattern recognizes gawk/mawk/nawk
PASS=$(parse_test "f2p_allowlist_gawk_mawk_nawk")
add_categorized 0.10 "$PASS" "pr_diff" "isInterpreterLikeAllowlistPattern recognizes gawk, mawk, nawk" "F2P"

# [pr_diff] (0.15): detectInterpreterInlineEvalArgv detects awk positional inline program
PASS=$(parse_test "f2p_detect_awk_positional")
add_categorized 0.15 "$PASS" "pr_diff" "detectInterpreterInlineEvalArgv detects awk inline program" "F2P"

# [pr_diff] (0.075): detectInterpreterInlineEvalArgv detects gawk with -F flag before program
PASS=$(parse_test "f2p_detect_gawk_with_F_flag")
add_categorized 0.075 "$PASS" "pr_diff" "detectInterpreterInlineEvalArgv detects gawk with -F flag" "F2P"

# ========== PASS-TO-PASS: Existing behavior preserved (0.15) ==========

# [pr_diff] (0.05): python3 still recognized as interpreter-like
PASS=$(parse_test "p2p_python_allowlist")
add_categorized 0.05 "$PASS" "pr_diff" "python3 still recognized as interpreter-like (pass-to-pass)" "P2P"

# [pr_diff] (0.05): python3 -c still detected as inline eval
PASS=$(parse_test "p2p_python_inline_eval")
add_categorized 0.05 "$PASS" "pr_diff" "python3 -c still detected as inline eval (pass-to-pass)" "P2P"

# [pr_diff] (0.05): awk -f not flagged as inline eval
PASS=$(parse_test "p2p_awk_file_not_inline")
add_categorized 0.05 "$PASS" "pr_diff" "awk -f script.awk not flagged as inline eval (pass-to-pass)" "P2P"

# ========== NEGATIVE: Non-interpreter programs must NOT match (0.20) ==========

# [pr_diff] (0.05): ls not falsely detected as interpreter-like
PASS=$(parse_test "neg_allowlist_ls")
add_categorized 0.05 "$PASS" "pr_diff" "ls not falsely detected as interpreter-like" "NEG"

# [pr_diff] (0.05): cat not falsely detected as interpreter-like
PASS=$(parse_test "neg_allowlist_cat")
add_categorized 0.05 "$PASS" "pr_diff" "cat not falsely detected as interpreter-like" "NEG"

# [pr_diff] (0.025): rg not falsely detected as interpreter-like
PASS=$(parse_test "neg_allowlist_rg")
add_categorized 0.025 "$PASS" "pr_diff" "rg not falsely detected as interpreter-like" "NEG"

# [pr_diff] (0.025): grep not falsely detected as interpreter-like
PASS=$(parse_test "neg_allowlist_grep")
add_categorized 0.025 "$PASS" "pr_diff" "grep not falsely detected as interpreter-like" "NEG"

# [pr_diff] (0.025): ls not detected as inline eval
PASS=$(parse_test "neg_detect_ls")
add_categorized 0.025 "$PASS" "pr_diff" "ls not detected as inline eval" "NEG"

# [pr_diff] (0.025): cat not detected as inline eval
PASS=$(parse_test "neg_detect_cat")
add_categorized 0.025 "$PASS" "pr_diff" "cat not detected as inline eval" "NEG"

# [pr_diff] (0.025): grep not detected as inline eval
PASS=$(parse_test "neg_detect_grep")
add_categorized 0.025 "$PASS" "pr_diff" "grep not detected as inline eval" "NEG"

# ========== STRUCTURAL: Integration wiring (0.05) ==========

# [pr_diff] (0.05): exec-approvals-allowlist.ts uses isInterpreterLikeAllowlistPattern
# WHY structural: collectAllowAlwaysPatterns requires complex mock objects to call directly
if grep -q 'isInterpreterLikeAllowlistPattern' "$ALLOWLIST_SRC" 2>/dev/null; then
    add_categorized 0.05 1 "pr_diff" "allowlist module uses isInterpreterLikeAllowlistPattern guard" "STRUCT"
else
    add_categorized 0.05 0 "pr_diff" "allowlist module uses isInterpreterLikeAllowlistPattern guard" "STRUCT"
fi

# ========== CONFIG-DERIVED: Agent config rule checks (0.10) ==========

# [agent_config] (0.05): "Never add @ts-nocheck" — CLAUDE.md:146 @ b7b46ad
if ! grep -q '@ts-nocheck' "$EVAL_SRC" 2>/dev/null && \
   ! grep -q '@ts-nocheck' "$ALLOWLIST_SRC" 2>/dev/null; then
    add_categorized 0.05 1 "agent_config" "No @ts-nocheck in modified files — CLAUDE.md:146" "CONFIG"
else
    add_categorized 0.05 0 "agent_config" "No @ts-nocheck in modified files — CLAUDE.md:146" "CONFIG"
fi

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144 @ b7b46ad
AWK_ANY_COUNT=$(grep -cE ':\s*any\b|<any>' "$EVAL_SRC" 2>/dev/null || true)
ALLOWLIST_ANY_COUNT=$(grep -cE ':\s*any\b|<any>' "$ALLOWLIST_SRC" 2>/dev/null || true)
if [ "$AWK_ANY_COUNT" = "0" ] && [ "$ALLOWLIST_ANY_COUNT" = "0" ]; then
    add_categorized 0.05 1 "agent_config" "No 'any' type annotations in modified files — CLAUDE.md:144" "CONFIG"
else
    add_categorized 0.05 0 "agent_config" "No 'any' type annotations in modified files — CLAUDE.md:144" "CONFIG"
fi

# ========== RESULTS ==========

echo "========================================="
echo "Test Results"
echo "========================================="
printf "$DETAILS"
echo "========================================="
echo "Score: $SCORE / $TOTAL"
echo "========================================="

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON with computed category scores
python3 -c "
import json
score = float('$SCORE')
data = {
    'reward': score,
    'f2p': float('$F2P_SCORE'),
    'p2p': float('$P2P_SCORE'),
    'negative': float('$NEG_SCORE'),
    'structural': float('$STRUCT_SCORE'),
    'config': float('$CONFIG_SCORE')
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
