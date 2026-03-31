#!/usr/bin/env bash
set +e
set -uo pipefail

PASS=0.0

cd /workspace/ruff

##############################################################################
# GATE: Core source files exist and code compiles
##############################################################################
RULE_FILE="crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs"
PREVIEW_FILE="crates/ruff_linter/src/preview.rs"

if [ ! -f "$RULE_FILE" ] || [ ! -f "$PREVIEW_FILE" ]; then
    echo "GATE FAIL: required source files missing"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# [pr_diff] (gate): cargo check must pass — can't test anything without compilation
echo "Running cargo check -p ruff_linter..."
if ! cargo check -p ruff_linter 2>&1; then
    echo "GATE FAIL: cargo check failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: compilation passed"

# Build ruff binary for behavioral testing
echo "Building ruff binary..."
cargo build --bin ruff 2>&1 || true
RUFF_BIN="./target/debug/ruff"
if [ ! -x "$RUFF_BIN" ]; then
    echo "GATE FAIL: could not build ruff binary"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: ruff binary built"

##############################################################################
# Create test files
##############################################################################

cat > /tmp/test_annotated_redef.py <<'PYEOF'
bar: int = 1
bar: int = 2
x: str = "hello"
x: str = "world"
PYEOF

cat > /tmp/test_single_pair.py <<'PYEOF'
myvar: float = 3.14
myvar: float = 2.72
PYEOF

cat > /tmp/test_fix_target.py <<'PYEOF'
bar: int = 1
bar: int = 2
PYEOF

cat > /tmp/test_plain_reassign.py <<'PYEOF'
y = 1
y = 2
PYEOF

cat > /tmp/test_mixed_assign.py <<'PYEOF'
z = 1
z: int = 2
w: int = 1
w = 2
PYEOF

cat > /tmp/test_used_between.py <<'PYEOF'
a: int = 1
print(a)
a: int = 2
PYEOF

##############################################################################
# FAIL-TO-PASS: Behavioral tests (0.70 total)
##############################################################################

# [pr_diff] (0.30): Annotated redeclarations flagged as F811 in preview mode
# WHY: This is the core bug — annotated assignment pairs should trigger F811.
OUTPUT=$($RUFF_BIN check --select F811 --preview --no-cache /tmp/test_annotated_redef.py 2>&1 || true)
F811_COUNT=$(echo "$OUTPUT" | grep -c 'F811' || echo "0")
if [ "$F811_COUNT" -ge 2 ]; then
    PASS=$(echo "$PASS + 0.30" | bc)
    echo "PASS [0.30]: Annotated redeclarations flagged ($F811_COUNT F811 violations)"
else
    echo "FAIL [0.30]: Annotated redeclarations not flagged (found $F811_COUNT, expected >=2)"
    echo "  Output: $OUTPUT"
fi

# [pr_diff] (0.15): Diagnostic output mentions correct variable names
# WHY: The diagnostic should identify which variables are redefined.
HAS_BAR=$(echo "$OUTPUT" | grep -ci 'bar' || echo "0")
HAS_X=$(echo "$OUTPUT" | grep -ci '`x`' || echo "0")
if [ "$HAS_BAR" -ge 1 ] && [ "$HAS_X" -ge 1 ]; then
    PASS=$(echo "$PASS + 0.15" | bc)
    echo "PASS [0.15]: Diagnostics mention correct variable names (bar, x)"
else
    echo "FAIL [0.15]: Diagnostics missing variable names (bar=$HAS_BAR, x=$HAS_X)"
fi

# [pr_diff] (0.15): --fix mode removes the shadowed (first) annotated assignment
# WHY: ruff's autofix for F811 should remove the unused first binding.
cp /tmp/test_fix_target.py /tmp/test_fix_work.py
$RUFF_BIN check --select F811 --preview --fix --no-cache /tmp/test_fix_work.py 2>&1 || true
FIXED_CONTENT=$(cat /tmp/test_fix_work.py)
# After fix: "bar: int = 1" should be removed, "bar: int = 2" should remain
if echo "$FIXED_CONTENT" | grep -q 'bar: int = 2' && ! echo "$FIXED_CONTENT" | grep -q 'bar: int = 1'; then
    PASS=$(echo "$PASS + 0.15" | bc)
    echo "PASS [0.15]: --fix correctly removes first annotated assignment"
else
    echo "FAIL [0.15]: --fix did not remove first annotated assignment"
    echo "  Fixed content: $FIXED_CONTENT"
fi

# [pr_diff] (0.10): Single annotated redeclaration pair also flagged
# WHY: Ensure the rule works for any pair, not just specific variable names.
OUTPUT_SINGLE=$($RUFF_BIN check --select F811 --preview --no-cache /tmp/test_single_pair.py 2>&1 || true)
F811_SINGLE=$(echo "$OUTPUT_SINGLE" | grep -c 'F811' || echo "0")
if [ "$F811_SINGLE" -ge 1 ]; then
    PASS=$(echo "$PASS + 0.10" | bc)
    echo "PASS [0.10]: Single annotated redeclaration pair flagged"
else
    echo "FAIL [0.10]: Single pair not flagged"
    echo "  Output: $OUTPUT_SINGLE"
fi

##############################################################################
# PASS-TO-PASS: Negative behavioral tests (0.13 total)
##############################################################################

# [pr_diff] (0.03): Plain reassignments NOT flagged
OUTPUT=$($RUFF_BIN check --select F811 --preview --no-cache /tmp/test_plain_reassign.py 2>&1 || true)
F811_COUNT=$(echo "$OUTPUT" | grep -c 'F811' || echo "0")
if [ "$F811_COUNT" -eq 0 ]; then
    PASS=$(echo "$PASS + 0.03" | bc)
    echo "PASS [0.03]: Plain reassignments correctly not flagged"
else
    echo "FAIL [0.03]: Plain reassignments incorrectly flagged ($F811_COUNT)"
fi

# [pr_diff] (0.02): Mixed assignments NOT flagged
OUTPUT=$($RUFF_BIN check --select F811 --preview --no-cache /tmp/test_mixed_assign.py 2>&1 || true)
F811_COUNT=$(echo "$OUTPUT" | grep -c 'F811' || echo "0")
if [ "$F811_COUNT" -eq 0 ]; then
    PASS=$(echo "$PASS + 0.02" | bc)
    echo "PASS [0.02]: Mixed assignments correctly not flagged"
else
    echo "FAIL [0.02]: Mixed assignments incorrectly flagged ($F811_COUNT)"
fi

# [pr_diff] (0.02): Used-between-assignments NOT flagged
OUTPUT=$($RUFF_BIN check --select F811 --preview --no-cache /tmp/test_used_between.py 2>&1 || true)
F811_COUNT=$(echo "$OUTPUT" | grep -c 'F811' || echo "0")
if [ "$F811_COUNT" -eq 0 ]; then
    PASS=$(echo "$PASS + 0.02" | bc)
    echo "PASS [0.02]: Used-between-assignments correctly not flagged"
else
    echo "FAIL [0.02]: Used-between-assignments incorrectly flagged ($F811_COUNT)"
fi

# [pr_diff] (0.03): Non-preview mode does NOT flag annotated redeclarations
OUTPUT=$($RUFF_BIN check --select F811 --no-cache /tmp/test_annotated_redef.py 2>&1 || true)
F811_COUNT=$(echo "$OUTPUT" | grep -c 'F811' || echo "0")
if [ "$F811_COUNT" -eq 0 ]; then
    PASS=$(echo "$PASS + 0.03" | bc)
    echo "PASS [0.03]: Non-preview mode correctly does not flag annotated redeclarations"
else
    echo "FAIL [0.03]: Non-preview mode incorrectly flags annotated redeclarations"
fi

# [pr_diff] (0.03): Existing F811 upstream tests still pass
echo "Running existing F811 tests..."
if cargo test -p ruff_linter -- f811 --test-threads=1 2>&1 | tail -5; then
    PASS=$(echo "$PASS + 0.03" | bc)
    echo "PASS [0.03]: Existing F811 tests pass"
else
    echo "FAIL [0.03]: Existing F811 tests broke"
fi

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ 29bf84e0
if ! grep -A1 'fn ' "$RULE_FILE" | grep -q '^\s*use '; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: Rust imports at file top, not in functions"
else
    echo "FAIL [0.05]: Rust import found inside a function body"
fi

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 29bf84e0
BASE_UNWRAPS=$(git show HEAD:crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$RULE_FILE" || echo "0")
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: No new .unwrap() calls added"
else
    echo "FAIL [0.05]: New .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi

##############################################################################
# Anti-stub / structural (0.07 total)
##############################################################################

# [pr_diff] (0.04): redefined_while_unused.rs not truncated
LINE_COUNT=$(wc -l < "$RULE_FILE")
if [ "$LINE_COUNT" -gt 200 ]; then
    PASS=$(echo "$PASS + 0.04" | bc)
    echo "PASS [0.04]: $RULE_FILE has $LINE_COUNT lines (not truncated)"
else
    echo "FAIL [0.04]: $RULE_FILE only has $LINE_COUNT lines (likely truncated)"
fi

# [pr_diff] (0.03): preview.rs not truncated
PREVIEW_LINES=$(wc -l < "$PREVIEW_FILE")
if [ "$PREVIEW_LINES" -gt 5 ]; then
    PASS=$(echo "$PASS + 0.03" | bc)
    echo "PASS [0.03]: $PREVIEW_FILE has $PREVIEW_LINES lines (not truncated)"
else
    echo "FAIL [0.03]: $PREVIEW_FILE only has $PREVIEW_LINES lines (likely truncated)"
fi

##############################################################################
# Final score
##############################################################################
SCORE=$(python3 -c "print(round(min(1.0, $PASS), 4))")
echo ""
echo "=== TOTAL: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
BEHAVIORAL_F2P=$(python3 -c "print(min(0.70, $PASS))")
python3 -c "
import json
reward = $SCORE
print(json.dumps({
    'reward': round(reward, 4),
    'behavioral': round(min(0.83, $PASS), 4),
    'regression': round(max(0, min(0.03, $PASS - 0.83)), 4),
    'config': round(max(0, min(0.10, $PASS - 0.86)), 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
