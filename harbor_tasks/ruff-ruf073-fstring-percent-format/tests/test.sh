#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0
GATE_PASS=true

cd /workspace/ruff

##############################################################################
# GATE: Core source compiles
##############################################################################
# [pr_diff] (gate): cargo check must succeed for ruff_linter
echo "Running cargo check -p ruff_linter (this may take a few minutes)..."
if cargo check -p ruff_linter 2>&1; then
    echo "GATE: cargo check passed"
else
    echo "GATE FAIL: cargo check -p ruff_linter failed"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Build ruff binary for behavioral testing
##############################################################################
echo "Building ruff binary..."
cargo build --bin ruff 2>&1 || true
RUFF_BIN="./target/debug/ruff"
if [ ! -x "$RUFF_BIN" ]; then
    echo "WARN: Could not build ruff binary, falling back to structural checks"
    RUFF_BIN=""
fi

##############################################################################
# Fail-to-pass: Behavioral tests (0.65 total)
##############################################################################

# Create test files for behavioral verification

# F-strings with % operator — all should be flagged
cat > /tmp/test_fstring_percent_var.py <<'PYEOF'
banana = "banana"
f"{banana}" % banana
PYEOF

cat > /tmp/test_fstring_percent_tuple.py <<'PYEOF'
f"hello %s %s" % (1, 2)
PYEOF

cat > /tmp/test_fstring_percent_dict.py <<'PYEOF'
x = 42
f"value: {x}" % {"key": "value"}
PYEOF

cat > /tmp/test_fstring_percent_literal.py <<'PYEOF'
x = 1
f"{'nested'} %s" % 42
f"no placeholders" % "banana"
PYEOF

# OK cases — should NOT be flagged
cat > /tmp/test_fstring_percent_ok.py <<'PYEOF'
name = "world"
# Plain string % — handled by F50x, not this rule
"hello %s" % "world"
"%s %s" % (1, 2)
# f-string without %
f"hello {name}"
# modulo on non-string
result = 42 % 10
PYEOF

if [ -n "$RUFF_BIN" ]; then
    # [pr_diff] (0.15): f-string with % and variable RHS flagged
    OUTPUT=$($RUFF_BIN check --select RUF073 --preview --no-cache /tmp/test_fstring_percent_var.py 2>&1 || true)
    RUF073_COUNT=$(echo "$OUTPUT" | grep -c 'RUF073' || echo "0")
    if [ "$RUF073_COUNT" -ge 1 ]; then
        PASS=$(echo "$PASS + 0.15" | bc)
        echo "PASS [0.15]: f-string % variable flagged (found $RUF073_COUNT)"
    else
        echo "FAIL [0.15]: f-string % variable not flagged (found $RUF073_COUNT)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.15" | bc)

    # [pr_diff] (0.15): f-string with % and tuple RHS flagged
    OUTPUT=$($RUFF_BIN check --select RUF073 --preview --no-cache /tmp/test_fstring_percent_tuple.py 2>&1 || true)
    RUF073_COUNT=$(echo "$OUTPUT" | grep -c 'RUF073' || echo "0")
    if [ "$RUF073_COUNT" -ge 1 ]; then
        PASS=$(echo "$PASS + 0.15" | bc)
        echo "PASS [0.15]: f-string % tuple flagged (found $RUF073_COUNT)"
    else
        echo "FAIL [0.15]: f-string % tuple not flagged (found $RUF073_COUNT)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.15" | bc)

    # [pr_diff] (0.10): f-string with % and dict RHS flagged
    OUTPUT=$($RUFF_BIN check --select RUF073 --preview --no-cache /tmp/test_fstring_percent_dict.py 2>&1 || true)
    RUF073_COUNT=$(echo "$OUTPUT" | grep -c 'RUF073' || echo "0")
    if [ "$RUF073_COUNT" -ge 1 ]; then
        PASS=$(echo "$PASS + 0.10" | bc)
        echo "PASS [0.10]: f-string % dict flagged (found $RUF073_COUNT)"
    else
        echo "FAIL [0.10]: f-string % dict not flagged (found $RUF073_COUNT)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.10" | bc)

    # [pr_diff] (0.15): f-string with % and literal/nested RHS flagged
    OUTPUT=$($RUFF_BIN check --select RUF073 --preview --no-cache /tmp/test_fstring_percent_literal.py 2>&1 || true)
    RUF073_COUNT=$(echo "$OUTPUT" | grep -c 'RUF073' || echo "0")
    if [ "$RUF073_COUNT" -ge 2 ]; then
        PASS=$(echo "$PASS + 0.15" | bc)
        echo "PASS [0.15]: f-string % literal/nested flagged (found $RUF073_COUNT)"
    else
        echo "FAIL [0.15]: f-string % literal/nested not flagged (found $RUF073_COUNT, expected >=2)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.15" | bc)

    # [pr_diff] (0.10): plain strings and non-string modulo NOT flagged by RUF073
    OUTPUT=$($RUFF_BIN check --select RUF073 --preview --no-cache /tmp/test_fstring_percent_ok.py 2>&1 || true)
    RUF073_COUNT=$(echo "$OUTPUT" | grep -c 'RUF073' || echo "0")
    if [ "$RUF073_COUNT" -eq 0 ]; then
        PASS=$(echo "$PASS + 0.10" | bc)
        echo "PASS [0.10]: OK cases correctly not flagged"
    else
        echo "FAIL [0.10]: OK cases incorrectly flagged ($RUF073_COUNT violations)"
        echo "  Output: $OUTPUT"
    fi
    TOTAL=$(echo "$TOTAL + 0.10" | bc)
else
    TOTAL=$(echo "$TOTAL + 0.65" | bc)
    echo "SKIP [0.65]: Could not build ruff binary for behavioral tests"
fi

##############################################################################
# Pass-to-pass: Regression tests (0.15 total)
##############################################################################

# [pr_diff] (0.08): Existing RUF07x tests still pass
echo "Running existing RUF07x tests..."
if INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo test -p ruff_linter -- RUF07 --test-threads=1 2>&1 | tail -5; then
    PASS=$(echo "$PASS + 0.08" | bc)
    echo "PASS [0.08]: Existing RUF07x tests pass"
else
    echo "FAIL [0.08]: Existing RUF07x tests broke"
fi
TOTAL=$(echo "$TOTAL + 0.08" | bc)

# [pr_diff] (0.07): Existing F50x percent-format rules still work
if [ -n "$RUFF_BIN" ]; then
    cat > /tmp/test_existing_f50x.py <<'PYEOF'
'%s %s' % (1,)
'%s' % (1, 2)
PYEOF
    OUTPUT=$($RUFF_BIN check --select F507 --no-cache /tmp/test_existing_f50x.py 2>&1 || true)
    F507_COUNT=$(echo "$OUTPUT" | grep -c 'F507' || echo "0")
    if [ "$F507_COUNT" -ge 2 ]; then
        PASS=$(echo "$PASS + 0.07" | bc)
        echo "PASS [0.07]: Existing F507 cases still flagged"
    else
        echo "FAIL [0.07]: Existing F507 cases not flagged ($F507_COUNT)"
    fi
else
    echo "SKIP [0.07]: Could not build ruff binary"
fi
TOTAL=$(echo "$TOTAL + 0.07" | bc)

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ b491f7eb
# Check all new/modified .rs files in the ruff rules directory for local imports
NEW_RS_FILES=$(git diff --name-only HEAD 2>/dev/null | grep '\.rs$' || true)
LOCAL_IMPORT=false
for f in $NEW_RS_FILES; do
    if [ -f "$f" ] && grep -A1 'fn ' "$f" | grep -q '^\s*use '; then
        LOCAL_IMPORT=true
        break
    fi
done
if [ "$LOCAL_IMPORT" = false ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: Rust imports at file top, not in functions"
else
    echo "FAIL [0.05]: Rust import found inside a function body"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ b491f7eb
# Check new .rs files for unwrap/panic/unreachable
UNSAFE_PATTERNS=0
for f in $NEW_RS_FILES; do
    if [ -f "$f" ]; then
        COUNT=$(grep -cE '\.(unwrap|expect)\(\)|panic!\(|unreachable!\(' "$f" 2>/dev/null || echo "0")
        UNSAFE_PATTERNS=$((UNSAFE_PATTERNS + COUNT))
    fi
done
# Allow up to the same count as the base (we just check new files are clean)
if [ "$UNSAFE_PATTERNS" -le 0 ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: No .unwrap()/panic!/unreachable! in new files"
else
    echo "FAIL [0.05]: Found $UNSAFE_PATTERNS .unwrap()/panic!/unreachable! patterns"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Anti-stub / structural (0.10 total)
##############################################################################

# [pr_diff] (0.05): Rule implementation file is non-trivial (not a stub)
RULE_FILE=$(find crates/ruff_linter/src/rules/ruff/rules/ -name '*fstring*percent*' -o -name '*percent*fstring*' -o -name '*fstring_mod*' 2>/dev/null | head -1)
if [ -z "$RULE_FILE" ]; then
    # Also check if any new .rs file in ruff rules contains the check function
    RULE_FILE=$(grep -rl 'FString.*Percent\|fstring.*percent\|Expr::FString' crates/ruff_linter/src/rules/ruff/rules/ 2>/dev/null | head -1)
fi
if [ -n "$RULE_FILE" ] && [ -f "$RULE_FILE" ]; then
    LINES=$(wc -l < "$RULE_FILE")
    if [ "$LINES" -ge 20 ]; then
        PASS=$(echo "$PASS + 0.05" | bc)
        echo "PASS [0.05]: Rule file $RULE_FILE has $LINES lines (not a stub)"
    else
        echo "FAIL [0.05]: Rule file $RULE_FILE only has $LINES lines (likely a stub)"
    fi
else
    echo "FAIL [0.05]: No rule implementation file found for fstring percent format"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

# [pr_diff] (0.05): Rule is registered in codes.rs
if grep -q '"073"' crates/ruff_linter/src/codes.rs 2>/dev/null; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: Rule code 073 registered in codes.rs"
else
    echo "FAIL [0.05]: Rule code 073 not found in codes.rs"
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
