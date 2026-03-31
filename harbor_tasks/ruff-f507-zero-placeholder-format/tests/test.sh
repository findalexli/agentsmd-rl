#!/usr/bin/env bash
set +e

PASS=0
TOTAL=100

cd /workspace/ruff

##############################################################################
# GATE: Core source file exists, compiles, and basic linting still works
##############################################################################
RULE_FILE="crates/ruff_linter/src/rules/pyflakes/rules/strings.rs"
if [ ! -f "$RULE_FILE" ]; then
    echo "GATE FAIL: $RULE_FILE does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Gate: strings.rs not truncated
LINE_COUNT=$(wc -l < "$RULE_FILE")
if [ "$LINE_COUNT" -le 500 ]; then
    echo "GATE FAIL: strings.rs only has $LINE_COUNT lines (likely truncated/stubbed)"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo "Building ruff binary (this may take a few minutes)..."
if ! cargo build --bin ruff 2>&1; then
    echo "GATE FAIL: cargo build failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

RUFF_BIN="./target/debug/ruff"
if [ ! -x "$RUFF_BIN" ]; then
    echo "GATE FAIL: ruff binary not executable"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Gate: correct format usage must NOT be flagged (sanity check)
cat > /tmp/test_gate_correct.py <<'PYEOF'
'%s' % 42
'%s %s' % (1, 2)
'%d items: %s' % (3, 'abc')
PYEOF
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_gate_correct.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -gt 0 ]; then
    echo "GATE FAIL: correct format usage is being false-positived ($F507_COUNT F507)"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: all gate checks passed"

##############################################################################
# FAIL-TO-PASS: Behavioral tests (70 points)
# These FAIL on the buggy base commit and PASS after a correct fix.
##############################################################################

# --- Test file: zero-placeholder format strings with literal RHS ---
cat > /tmp/test_f2p_literal.py <<'PYEOF'
'hello' % 42
'' % 42
'hello' % (1,)
PYEOF

# [pr_diff] (0.25): Zero-placeholder with literal RHS flagged as F507
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_f2p_literal.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -ge 3 ]; then
    PASS=$((PASS + 25))
    echo "PASS [0.25]: Literal RHS flagged ($F507_COUNT F507 violations)"
else
    echo "FAIL [0.25]: Literal RHS not flagged ($F507_COUNT, expected >=3)"
fi

# --- Test file: zero-placeholder with variable RHS ---
cat > /tmp/test_f2p_variable.py <<'PYEOF'
banana = 42
'hello' % banana
'' % banana
PYEOF

# [pr_diff] (0.25): Zero-placeholder with variable RHS flagged as F507
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_f2p_variable.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -ge 2 ]; then
    PASS=$((PASS + 25))
    echo "PASS [0.25]: Variable RHS flagged ($F507_COUNT F507 violations)"
else
    echo "FAIL [0.25]: Variable RHS not flagged ($F507_COUNT, expected >=2)"
fi

# --- Test file: zero-placeholder with dynamic RHS (calls, attrs) ---
cat > /tmp/test_f2p_dynamic.py <<'PYEOF'
'hello' % unknown_var
'hello' % get_value()
'hello' % obj.attr
PYEOF

# [pr_diff] (0.20): Zero-placeholder with dynamic RHS flagged as F507
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_f2p_dynamic.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -ge 3 ]; then
    PASS=$((PASS + 20))
    echo "PASS [0.20]: Dynamic RHS flagged ($F507_COUNT F507 violations)"
else
    echo "FAIL [0.20]: Dynamic RHS not flagged ($F507_COUNT, expected >=3)"
fi

##############################################################################
# PASS-TO-PASS: Regression tests (15 points)
# These PASS on the base commit and must still PASS after the fix.
##############################################################################

# --- Test file: empty tuple RHS should NOT be flagged ---
cat > /tmp/test_p2p_empty_tuple.py <<'PYEOF'
'hello' % ()
PYEOF

# [pr_diff] (0.05): Empty tuple RHS not flagged (valid at runtime)
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_p2p_empty_tuple.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -eq 0 ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: Empty tuple RHS correctly not flagged"
else
    echo "FAIL [0.05]: Empty tuple RHS incorrectly flagged ($F507_COUNT)"
fi

# --- Test file: existing non-zero-placeholder mismatches still flagged ---
cat > /tmp/test_p2p_existing.py <<'PYEOF'
'%s %s' % (1,)
'%s' % (1, 2)
PYEOF

# [pr_diff] (0.10): Existing F507 mismatch cases still detected
OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_p2p_existing.py 2>&1 || true)
F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
if [ "$F507_COUNT" -ge 2 ]; then
    PASS=$((PASS + 10))
    echo "PASS [0.10]: Existing F507 mismatches still flagged ($F507_COUNT)"
else
    echo "FAIL [0.10]: Existing F507 mismatches broken ($F507_COUNT, expected >=2)"
fi

##############################################################################
# CONFIG-DERIVED: Agent config checks (10 points)
##############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top" — AGENTS.md:76 @ 690ef81f
if ! grep -A1 'fn ' "$RULE_FILE" | grep -q '^\s*use '; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: Rust imports at file top, not in functions"
else
    echo "FAIL [0.05]: Rust import found inside a function body"
fi

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 690ef81f
BASE_UNWRAPS=$(git show HEAD:crates/ruff_linter/src/rules/pyflakes/rules/strings.rs 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$RULE_FILE" || echo "0")
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: No new .unwrap() calls added"
else
    echo "FAIL [0.05]: New .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi

##############################################################################
# ANTI-STUB: Structural sanity (5 points)
##############################################################################

# [pr_diff] (0.05): F50x.py fixture not truncated
FIXTURE_FILE="crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py"
if [ -f "$FIXTURE_FILE" ]; then
    FIXTURE_LINES=$(wc -l < "$FIXTURE_FILE")
    if [ "$FIXTURE_LINES" -gt 50 ]; then
        PASS=$((PASS + 5))
        echo "PASS [0.05]: $FIXTURE_FILE has $FIXTURE_LINES lines (not truncated)"
    else
        echo "FAIL [0.05]: $FIXTURE_FILE only has $FIXTURE_LINES lines (likely truncated)"
    fi
else
    echo "FAIL [0.05]: $FIXTURE_FILE does not exist"
fi

##############################################################################
# Final score
##############################################################################
SCORE=$(python3 -c "print(round(min(1.0, $PASS / $TOTAL), 4))")

echo ""
echo "=== TOTAL: $SCORE ($PASS / $TOTAL points) ==="
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
reward = round(min(1.0, $PASS / 100.0), 4)
# Proportional breakdown based on check categories
f2p = min(70, $PASS) / 100.0
p2p = min(15, max(0, $PASS - 70)) / 100.0
cfg = min(10, max(0, $PASS - 85)) / 100.0
print(json.dumps({
    'reward': reward,
    'behavioral': round(f2p, 4),
    'regression': round(p2p, 4),
    'config': round(cfg, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
