#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0
GATE_PASS=true

cd /workspace/ruff

##############################################################################
# GATE: Core source file exists and is valid Rust
##############################################################################
# [pr_diff] (gate): enumerate_for_loop.rs must exist
RULE_FILE="crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs"
if [ ! -f "$RULE_FILE" ]; then
    echo "GATE FAIL: $RULE_FILE does not exist"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: source file checks passed"

##############################################################################
# Fail-to-pass: Behavioral tests (0.65 total)
##############################################################################

# [pr_diff] (0.20): Code compiles — cargo check on ruff_linter
echo "Running cargo check -p ruff_linter (this may take a few minutes)..."
if cargo check -p ruff_linter 2>&1; then
    PASS=$(echo "$PASS + 0.20" | bc)
    echo "PASS [0.20]: cargo check -p ruff_linter succeeded"
else
    echo "FAIL [0.20]: cargo check -p ruff_linter failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
TOTAL=$(echo "$TOTAL + 0.20" | bc)

# Build ruff binary for behavioral testing
echo "Building ruff binary..."
cargo build --bin ruff 2>&1 || true
RUFF_BIN="./target/debug/ruff"
if [ ! -x "$RUFF_BIN" ]; then
    echo "WARN: Could not build ruff binary, falling back to structural checks"
    RUFF_BIN=""
fi

# Create test files for behavioral verification

# Test 1: Sibling loops with the same counter variable — both should be flagged
cat > /tmp/test_sibling_loops.py <<'PYEOF'
def func():
    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1

    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1
PYEOF

# Test 2: enumerate() loop followed by manual counter — second should be flagged
cat > /tmp/test_enumerate_then_manual.py <<'PYEOF'
def func():
    for i, val in enumerate([1, 2, 3]):
        print(f"{i}: {val}")

    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1
PYEOF

# Test 3: Single loop with counter — should still be flagged (existing behavior)
cat > /tmp/test_single_loop.py <<'PYEOF'
def func():
    idx = 0
    for x in range(10):
        print(idx)
        idx += 1
PYEOF

# Test 4: Counter used after loop — should NOT be flagged (existing OK behavior)
cat > /tmp/test_used_after.py <<'PYEOF'
def func():
    i = 0
    for val in [1, 2, 3]:
        print(f"{i}: {val}")
        i += 1
    print(f"Total: {i}")
PYEOF

if [ -n "$RUFF_BIN" ]; then
    # [pr_diff] (0.20): Sibling loops — both flagged with SIM113
    OUTPUT=$($RUFF_BIN check --select SIM113 --no-cache /tmp/test_sibling_loops.py 2>&1 || true)
    SIM_COUNT=$(echo "$OUTPUT" | grep -c 'SIM113' || echo "0")
    if [ "$SIM_COUNT" -ge 2 ]; then
        PASS=$(echo "$PASS + 0.20" | bc)
        echo "PASS [0.20]: Sibling loops both flagged (found $SIM_COUNT SIM113 violations)"
    else
        echo "FAIL [0.20]: Sibling loops not both flagged (found $SIM_COUNT SIM113 violations, expected 2)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.20" | bc)

    # [pr_diff] (0.15): enumerate-then-manual pattern — second loop flagged
    OUTPUT=$($RUFF_BIN check --select SIM113 --no-cache /tmp/test_enumerate_then_manual.py 2>&1 || true)
    SIM_COUNT=$(echo "$OUTPUT" | grep -c 'SIM113' || echo "0")
    if [ "$SIM_COUNT" -ge 1 ]; then
        PASS=$(echo "$PASS + 0.15" | bc)
        echo "PASS [0.15]: enumerate-then-manual flagged (found $SIM_COUNT SIM113 violations)"
    else
        echo "FAIL [0.15]: enumerate-then-manual not flagged (found $SIM_COUNT SIM113 violations)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.15" | bc)

    # [pr_diff] (0.10): Single loop still flagged (existing behavior preserved)
    OUTPUT=$($RUFF_BIN check --select SIM113 --no-cache /tmp/test_single_loop.py 2>&1 || true)
    SIM_COUNT=$(echo "$OUTPUT" | grep -c 'SIM113' || echo "0")
    if [ "$SIM_COUNT" -ge 1 ]; then
        PASS=$(echo "$PASS + 0.10" | bc)
        echo "PASS [0.10]: Single loop still flagged correctly"
    else
        echo "FAIL [0.10]: Single loop no longer flagged (regression)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.10" | bc)
else
    TOTAL=$(echo "$TOTAL + 0.45" | bc)
    echo "SKIP [0.45]: Could not build ruff binary for behavioral tests"
fi

##############################################################################
# Pass-to-pass: Regression tests (0.15 total)
##############################################################################

# [pr_diff] (0.08): Counter used after loop — should NOT be flagged
if [ -n "$RUFF_BIN" ]; then
    OUTPUT=$($RUFF_BIN check --select SIM113 --no-cache /tmp/test_used_after.py 2>&1 || true)
    SIM_COUNT=$(echo "$OUTPUT" | grep -c 'SIM113' || echo "0")
    if [ "$SIM_COUNT" -eq 0 ]; then
        PASS=$(echo "$PASS + 0.08" | bc)
        echo "PASS [0.08]: Counter used after loop correctly not flagged"
    else
        echo "FAIL [0.08]: Counter used after loop incorrectly flagged"
    fi
else
    echo "SKIP [0.08]: Could not build ruff binary"
fi
TOTAL=$(echo "$TOTAL + 0.08" | bc)

# [pr_diff] (0.07): Existing SIM113 tests pass
echo "Running existing SIM113 tests..."
if INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo test -p ruff_linter -- SIM113 --test-threads=1 2>&1 | tail -5; then
    PASS=$(echo "$PASS + 0.07" | bc)
    echo "PASS [0.07]: Existing SIM113 tests pass"
else
    echo "FAIL [0.07]: Existing SIM113 tests broke"
fi
TOTAL=$(echo "$TOTAL + 0.07" | bc)

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ 5f7e0346
# Verify no new imports inside function bodies in enumerate_for_loop.rs
if ! grep -A1 'fn ' "$RULE_FILE" | grep -q '^\s*use '; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: Rust imports at file top, not in functions"
else
    echo "FAIL [0.05]: Rust import found inside a function body"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 5f7e0346
BASE_UNWRAPS=$(git show HEAD:crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$RULE_FILE" || echo "0")
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: no new .unwrap() calls added"
else
    echo "FAIL [0.05]: new .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Anti-stub / structural (0.10 total)
##############################################################################

# [pr_diff] (0.05): enumerate_for_loop.rs not truncated
LINE_COUNT=$(wc -l < "$RULE_FILE")
if [ "$LINE_COUNT" -gt 100 ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: $RULE_FILE has $LINE_COUNT lines (not truncated)"
else
    echo "FAIL [0.05]: $RULE_FILE only has $LINE_COUNT lines (likely truncated)"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Test fixture file was updated with new test cases
FIXTURE="crates/ruff_linter/resources/test/fixtures/flake8_simplify/SIM113.py"
if [ -f "$FIXTURE" ]; then
    FIXTURE_LINES=$(wc -l < "$FIXTURE")
    if [ "$FIXTURE_LINES" -gt 200 ]; then
        PASS=$(echo "$PASS + 0.05" | bc)
        echo "PASS [0.05]: SIM113.py fixture has $FIXTURE_LINES lines (updated)"
    else
        echo "FAIL [0.05]: SIM113.py fixture only has $FIXTURE_LINES lines (likely not updated)"
    fi
else
    echo "FAIL [0.05]: SIM113.py fixture not found"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Final score
##############################################################################
SCORE=$(python3 -c "print(round(min(1.0, $PASS), 4))")
echo ""
echo "=== TOTAL: $SCORE / $TOTAL ==="
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
reward = $SCORE
behavioral = min(0.65, $PASS)
regression = min(0.15, max(0, $PASS - 0.65))
config = min(0.10, max(0, $PASS - 0.80))
structural = min(0.10, max(0, $PASS - 0.90))
print(json.dumps({'reward': round(reward, 4), 'behavioral': round(min(behavioral, 0.65), 4), 'regression': round(min(regression, 0.15), 4), 'config': round(min(config, 0.10), 4), 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
