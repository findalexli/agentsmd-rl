#!/usr/bin/env bash
set +e
set -uo pipefail

TOTAL=0
PASS=0
GATE_PASS=true

cd /workspace/ruff

##############################################################################
# GATE: Cargo.toml specifies imara-diff 0.2.x and format_dev.rs exists
##############################################################################
# [pr_diff] (gate): Version must be upgraded to 0.2.x
if ! grep -qE 'imara-diff\s*=\s*\{\s*version\s*=\s*"0\.2' Cargo.toml 2>/dev/null; then
    echo "GATE FAIL: Cargo.toml does not specify imara-diff 0.2.x"
    GATE_PASS=false
fi

FMT_DEV="crates/ruff_dev/src/format_dev.rs"
if [ ! -f "$FMT_DEV" ]; then
    echo "GATE FAIL: $FMT_DEV does not exist"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: version and file checks passed"

##############################################################################
# Fail-to-pass: cargo check compiles with imara-diff 0.2.x (0.65)
##############################################################################
# [pr_diff] (0.65): Code compiles with imara-diff 0.2.x
# WHY cargo check: This is a Rust crate — compilation IS the behavioral test.
# The old 0.1.x API (diff(), Counter sink, intern::InternedInput) does not
# exist in 0.2.0, so cargo check fails unless the migration is correct.
echo "Running cargo check -p ruff_dev (this may take a few minutes)..."
if cargo check -p ruff_dev 2>&1; then
    PASS=$((PASS + 65))
    echo "PASS [0.65]: cargo check -p ruff_dev succeeded"
else
    echo "FAIL [0.65]: cargo check -p ruff_dev failed — API migration incorrect"
fi
TOTAL=$((TOTAL + 65))

##############################################################################
# Pass-to-pass: cargo check on dependent crates still works (0.10)
##############################################################################
# [pr_diff] (0.10): Other crates that depend on ruff_dev still compile
# This catches regressions like accidentally removing pub items or breaking
# the module interface.
echo "Running cargo check -p ruff_cli (regression check)..."
if cargo check -p ruff 2>&1; then
    PASS=$((PASS + 10))
    echo "PASS [0.10]: cargo check -p ruff succeeded (no regressions)"
else
    echo "FAIL [0.10]: cargo check -p ruff failed — regression introduced"
fi
TOTAL=$((TOTAL + 10))

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ 459f2022
# Verify no imara_diff imports inside function bodies
if ! grep -A1 'fn ' "$FMT_DEV" | grep -q 'use imara_diff'; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: imara_diff imports at file top, not in functions"
else
    echo "FAIL [0.05]: imara_diff imported inside a function body"
fi
TOTAL=$((TOTAL + 5))

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 459f2022
# Check no NEW unwrap/panic was added (compare to base)
BASE_UNWRAPS=$(git show HEAD:crates/ruff_dev/src/format_dev.rs 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$FMT_DEV" || echo "0")
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$((PASS + 5))
    echo "PASS [0.05]: no new .unwrap() calls added"
else
    echo "FAIL [0.05]: new .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi
TOTAL=$((TOTAL + 5))

##############################################################################
# Anti-stub / structural (0.15 total)
##############################################################################

# [pr_diff] (0.08): format_dev.rs not truncated or stubbed out
LINE_COUNT=$(wc -l < "$FMT_DEV")
if [ "$LINE_COUNT" -gt 200 ]; then
    PASS=$((PASS + 8))
    echo "PASS [0.08]: format_dev.rs has $LINE_COUNT lines (not truncated)"
else
    echo "FAIL [0.08]: format_dev.rs only has $LINE_COUNT lines (likely truncated)"
fi
TOTAL=$((TOTAL + 8))

# [pr_diff] (0.07): Statistics struct and diff-related methods still present
if grep -q 'pub(crate) struct Statistics' "$FMT_DEV" && \
   grep -q 'fn from_versions' "$FMT_DEV" && \
   grep -q 'fn similarity_index' "$FMT_DEV" && \
   grep -q 'fn jaccard_index' "$FMT_DEV"; then
    PASS=$((PASS + 7))
    echo "PASS [0.07]: Statistics struct and diff methods present"
else
    echo "FAIL [0.07]: Statistics struct or diff methods missing"
fi
TOTAL=$((TOTAL + 7))

##############################################################################
# Final score
##############################################################################
SCORE=$(python3 -c "print(round(min(1.0, $PASS / 100.0), 4))")
echo ""
echo "=== TOTAL: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
total = $PASS / 100.0
behavioral = min(0.75, total)
regression_start = 0.75
config_start = 0.85
structural_start = 0.90
regression = min(0.10, max(0, total - 0.65) if total > 0.65 else 0)
config = min(0.10, max(0, total - 0.75) if total > 0.75 else 0)
style = 0.0
print(json.dumps({
    'reward': round(min(1.0, total), 4),
    'behavioral': round(min(0.75, $PASS / 100.0 if $PASS <= 75 else 0.75), 4),
    'regression': round(min(0.10, max(0, ($PASS - 75) / 100.0)), 4),
    'config': round(min(0.10, max(0, ($PASS - 85) / 100.0)), 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
