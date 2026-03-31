#!/usr/bin/env bash
set +e  # Don't exit on test failures
SCORE=0
REPO=/workspace/ruff

# ── GATE (0.00): Rust compilation check ────────────────────────────
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
if ! cargo check -p ty_python_semantic --quiet 2>&1; then
    echo "GATE FAILED: code does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ── Helper: build ty binary ─────────────────────────────────────────
echo "=== Building ty binary (incremental) ==="
if ! cargo build --bin ty --quiet 2>&1; then
    echo "BUILD FAILED: cannot build ty binary"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
TY="$REPO/target/debug/ty"

# ── Create test Python files ────────────────────────────────────────
cat > /tmp/test_mismatch1.py <<'PYEOF'
from typing import TypedDict

BadTypedDict = TypedDict("WrongName", {"name": str})
PYEOF

cat > /tmp/test_mismatch2.py <<'PYEOF'
from typing_extensions import TypedDict

AnotherBad = TypedDict("Mismatch", {"x": int, "y": str})
PYEOF

cat > /tmp/test_mismatch3.py <<'PYEOF'
from typing import TypedDict

Foo = TypedDict("Bar", {"a": int})
PYEOF

cat > /tmp/test_correct.py <<'PYEOF'
from typing import TypedDict

GoodTypedDict = TypedDict("GoodTypedDict", {"name": str})
PYEOF

cat > /tmp/test_class_syntax.py <<'PYEOF'
from typing import TypedDict

class MyDict(TypedDict):
    name: str
    age: int
PYEOF

# ── Run ty on all test files ───────────────────────────────────────
echo "=== Running ty check on test files ==="
OUTPUT1=$("$TY" check /tmp/test_mismatch1.py 2>&1 || true)
OUTPUT2=$("$TY" check /tmp/test_mismatch2.py 2>&1 || true)
OUTPUT3=$("$TY" check /tmp/test_mismatch3.py 2>&1 || true)
OUTPUT_CORRECT=$("$TY" check /tmp/test_correct.py 2>&1 || true)
OUTPUT_CLASS=$("$TY" check /tmp/test_class_syntax.py 2>&1 || true)

echo "--- mismatch1 output ---"
echo "$OUTPUT1"
echo "--- mismatch2 output ---"
echo "$OUTPUT2"
echo "--- mismatch3 output ---"
echo "$OUTPUT3"
echo "--- correct output ---"
echo "$OUTPUT_CORRECT"
echo "--- class syntax output ---"
echo "$OUTPUT_CLASS"

# ── BEHAVIORAL 1 (0.25): Mismatched name produces any diagnostic ──
# [pr_diff] (0.25): TypedDict("WrongName") assigned to BadTypedDict triggers a diagnostic
# Accepts ANY valid diagnostic (error or warning) — not tied to specific message text
echo "=== BEHAVIORAL 1: mismatched name produces diagnostic ==="
DIAG_COUNT1=$(echo "$OUTPUT1" | grep -cE "(error|warning)\[" || true)
if [ "$DIAG_COUNT1" -gt 0 ]; then
    echo "PASS: mismatch diagnostic found ($DIAG_COUNT1 diagnostics)"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "FAIL: no diagnostic on mismatched TypedDict"
fi

# ── BEHAVIORAL 2 (0.20): typing_extensions mismatch also diagnosed ─
# [pr_diff] (0.20): TypedDict("Mismatch") from typing_extensions assigned to AnotherBad
echo "=== BEHAVIORAL 2: typing_extensions mismatch ==="
DIAG_COUNT2=$(echo "$OUTPUT2" | grep -cE "(error|warning)\[" || true)
if [ "$DIAG_COUNT2" -gt 0 ]; then
    echo "PASS: typing_extensions mismatch diagnostic found"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL: no diagnostic for typing_extensions mismatch"
fi

# ── BEHAVIORAL 3 (0.10): Third independent mismatch case ──────────
# [pr_diff] (0.10): Foo = TypedDict("Bar", ...) triggers diagnostic
echo "=== BEHAVIORAL 3: third mismatch case (Foo/Bar) ==="
DIAG_COUNT3=$(echo "$OUTPUT3" | grep -cE "(error|warning)\[" || true)
if [ "$DIAG_COUNT3" -gt 0 ]; then
    echo "PASS: Foo/Bar mismatch diagnostic found"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: no diagnostic for Foo/Bar mismatch"
fi

# ── BEHAVIORAL 4 (0.10): Diagnostic mentions both names ───────────
# [agent_config] (0.10): "error messages concise" — AGENTS.md:83 @ ca3343e4
# The diagnostic should include both the string name and the variable name
echo "=== BEHAVIORAL 4: diagnostic quality — mentions both names ==="
if echo "$OUTPUT1" | grep -q "WrongName" && echo "$OUTPUT1" | grep -q "BadTypedDict"; then
    echo "PASS: diagnostic mentions both WrongName and BadTypedDict"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: diagnostic missing one or both names"
fi

# ── PASS-TO-PASS 1 (0.10): Correct functional TypedDict not flagged ─
# [pr_diff] (0.10): TypedDict("GoodTypedDict") assigned to GoodTypedDict is accepted
echo "=== P2P 1: correct functional TypedDict accepted ==="
CORRECT_DIAG=$(echo "$OUTPUT_CORRECT" | grep -cE "(error|warning)\[" || true)
if [ "$CORRECT_DIAG" -eq 0 ]; then
    echo "PASS: correct name accepted without diagnostic"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: false positive — correct name incorrectly flagged"
fi

# ── PASS-TO-PASS 2 (0.10): Class-based TypedDict not broken ───────
# [pr_diff] (0.10): class MyDict(TypedDict) syntax unaffected by change
echo "=== P2P 2: class-based TypedDict syntax unaffected ==="
CLASS_DIAG=$(echo "$OUTPUT_CLASS" | grep -cE "(error|warning)\[" || true)
if [ "$CLASS_DIAG" -eq 0 ]; then
    echo "PASS: class-based TypedDict syntax unaffected"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: class-based TypedDict broken by changes"
fi

# ── REGRESSION (0.15): Upstream typed_dict mdtest suite ────────────
# [repo_tests] (0.15): Existing typed_dict mdtest assertions still pass
echo "=== REGRESSION: upstream typed_dict mdtest ==="
cd "$REPO"
MDTEST_OUTPUT=$(MDTEST_TEST_FILTER=typed_dict cargo test -p ty_python_semantic --test mdtest 2>&1 || true)
echo "$MDTEST_OUTPUT" | tail -20
if echo "$MDTEST_OUTPUT" | grep -qE "test result: ok|passed"; then
    echo "PASS: upstream typed_dict mdtest passes"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: upstream typed_dict mdtest failures"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores for reward.json
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.65), 4))")
REGRESSION=$(python3 -c "print(round(min(max($SCORE - 0.65, 0), 0.35), 4))")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
