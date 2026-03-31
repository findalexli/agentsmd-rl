#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
TARGET="crates/ty_python_semantic/src/types.rs"

cd /workspace/ruff 2>/dev/null || cd /repo

echo "=== ty Materialize Divergent Alias Fix ==="

# ── GATE: File exists and crate compiles ────────────────────────────────
# [pr_diff] (gate): Modified file must exist
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# [pr_diff] (gate): ty must compile
echo "Building ty..."
if ! cargo build --bin ty 2>&1; then
    echo "GATE FAIL: cargo build --bin ty failed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: ty compiles"

TY_BIN=$(cargo metadata --format-version=1 --no-deps 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['target_directory'])" 2>/dev/null)/debug/ty
if [ ! -x "$TY_BIN" ]; then
    TY_BIN="./target/debug/ty"
fi

TESTDIR=$(mktemp -d)

# ── Fail-to-pass 1: recursive Callable type alias doesn't crash ────────

cat > "$TESTDIR/test_recursive_callable.py" << 'PYEOF'
from typing_extensions import TypeGuard, TypeIs
from collections.abc import Callable

type CallableIs = TypeIs[Callable[[], CallableIs]]
type CallableGuard = TypeGuard[Callable[[], CallableGuard]]

x: object = CallableIs
y: object = CallableGuard
PYEOF

echo ""
echo "Running ty check on recursive Callable type aliases..."
# [pr_diff] (0.40): Recursive Callable aliases with TypeIs/TypeGuard resolve without crash
TY_EXIT=0
TY_OUTPUT=$(timeout 60 "$TY_BIN" check --python-version 3.12 "$TESTDIR/test_recursive_callable.py" 2>&1) || TY_EXIT=$?
echo "$TY_OUTPUT"

if [ "$TY_EXIT" -le 1 ]; then
    echo "PASS (0.40): ty completed without crash on recursive Callable aliases"
    SCORE=$(python3 -c "print($SCORE + 0.40)")
else
    echo "FAIL (0.40): ty crashed or timed out (exit=$TY_EXIT)"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.40)")

# ── Fail-to-pass 2: no spurious cyclic-type-alias-definition on Callable-wrapped aliases ──

cat > "$TESTDIR/test_no_cyclic_error.py" << 'PYEOF'
from typing_extensions import TypeGuard, TypeIs
from collections.abc import Callable

type CallableIs = TypeIs[Callable[[], CallableIs]]
type CallableGuard = TypeGuard[Callable[[], CallableGuard]]

# These are valid recursive types — they should NOT trigger cyclic-type-alias-definition
def use_is(x: CallableIs) -> None:
    pass

def use_guard(x: CallableGuard) -> None:
    pass
PYEOF

echo ""
echo "Running ty check — Callable-wrapped aliases should not be flagged as cyclic..."
# [pr_diff] (0.25): Callable-wrapped recursive aliases are not flagged as cyclic
TY_EXIT2=0
TY_OUTPUT2=$(timeout 60 "$TY_BIN" check --python-version 3.12 "$TESTDIR/test_no_cyclic_error.py" 2>&1) || TY_EXIT2=$?
echo "$TY_OUTPUT2"

if [ "$TY_EXIT2" -le 1 ] && ! echo "$TY_OUTPUT2" | grep -q 'cyclic-type-alias-definition.*CallableIs\|cyclic-type-alias-definition.*CallableGuard'; then
    echo "PASS (0.25): Callable-wrapped aliases not flagged as cyclic"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "FAIL (0.25): Callable-wrapped aliases incorrectly flagged or crashed"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")

# ── Pass-to-pass: direct recursive TypeIs still flagged as cyclic ──────

cat > "$TESTDIR/test_direct_cyclic.py" << 'PYEOF'
from typing_extensions import TypeIs

type RecursiveIs = TypeIs[RecursiveIs]
PYEOF

echo ""
echo "Running ty check — direct recursive TypeIs should still be flagged as cyclic..."
# [pr_diff] (0.15): Direct recursive TypeIs[Self] still correctly produces cyclic-type-alias-definition
TY_EXIT3=0
TY_OUTPUT3=$(timeout 60 "$TY_BIN" check --python-version 3.12 "$TESTDIR/test_direct_cyclic.py" 2>&1) || TY_EXIT3=$?
echo "$TY_OUTPUT3"

if echo "$TY_OUTPUT3" | grep -q 'cyclic-type-alias-definition'; then
    echo "PASS (0.15): direct recursive TypeIs still flagged as cyclic"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL (0.15): direct recursive TypeIs no longer flagged as cyclic"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

# ── Config-derived checks ──────────────────────────────────────────────

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76
DIFF=$(git diff HEAD 2>/dev/null || true)
if [ -z "$DIFF" ]; then
    DIFF=$(git diff HEAD~1 2>/dev/null || true)
fi
NEW_LOCAL_USE=$(echo "$DIFF" | grep '^+' | grep -v '^+++' | grep -cE '^\+\s{4,}use\s+' || true)
if [ "$NEW_LOCAL_USE" -eq 0 ]; then
    echo "PASS (0.05): No new local imports in functions (AGENTS.md:76)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): Found $NEW_LOCAL_USE new local imports in functions"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79
NEW_UNWRAPS=$(echo "$DIFF" | grep '^+' | grep -v '^+++' | grep -cE '\.unwrap\(\)|panic!\(|unreachable!\(' || true)
if [ "$NEW_UNWRAPS" -eq 0 ]; then
    echo "PASS (0.05): No new unwrap()/panic!/unreachable! in diff"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): Found $NEW_UNWRAPS new unwrap()/panic!/unreachable! calls"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# ── Anti-stub check ────────────────────────────────────────────────────

# [static] (0.10): Target file has meaningful content (not stubbed/gutted)
LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -ge 5000 ]; then
    echo "PASS (0.10): File has meaningful content ($LINE_COUNT lines)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): File appears stubbed ($LINE_COUNT lines, expected >=5000)"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# Clean up
rm -rf "$TESTDIR"

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "Total: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed reward breakdown
python3 -c "
import json
score = float('$SCORE')
data = {'reward': score}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
