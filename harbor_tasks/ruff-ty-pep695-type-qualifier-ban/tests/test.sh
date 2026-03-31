#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
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

# Test file: type qualifiers in PEP 695 aliases (should all error)
cat > /tmp/test_pep695_qualifiers.py <<'PYEOF'
from typing_extensions import ClassVar, Final, Required, NotRequired, ReadOnly
from dataclasses import InitVar

type Bad1 = ClassVar[str]
type Bad2 = ClassVar
type Bad3 = Final[int]
type Bad4 = Final
type Bad5 = Required[int]
type Bad6 = NotRequired[int]
type Bad7 = ReadOnly[int]
type Bad8 = InitVar[int]
type Bad9 = InitVar
PYEOF

# Test file: valid PEP 695 aliases (should produce no errors)
cat > /tmp/test_pep695_valid.py <<'PYEOF'
type IntOrStr = int | str
type OptionalInt = int | None
type ListOf[T] = list[T]
type DictOf[K, V] = dict[K, V]
PYEOF

# Test file: ClassVar in annotation (not a type alias) — still valid
cat > /tmp/test_classvar_annotation.py <<'PYEOF'
from typing import ClassVar

class Foo:
    x: ClassVar[int] = 42
PYEOF

# ── BEHAVIORAL 1 (0.25): ClassVar rejected in PEP 695 alias ────────
# [pr_diff] (0.25): type Bad1 = ClassVar[str] must produce invalid-type-form
echo "=== BEHAVIORAL 1: ClassVar[str] rejected in type alias ==="
OUTPUT=$("$TY" check /tmp/test_pep695_qualifiers.py 2>&1 || true)
echo "$OUTPUT"
CLASSVAR_ERRORS=$(echo "$OUTPUT" | grep -c "invalid-type-form" || true)
# We expect at least 2 ClassVar errors (subscripted + bare)
if [ "$CLASSVAR_ERRORS" -ge 2 ]; then
    echo "PASS: ClassVar flagged in PEP 695 aliases"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "FAIL: expected >=2 ClassVar invalid-type-form errors, got $CLASSVAR_ERRORS"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")

# ── BEHAVIORAL 2 (0.20): Final rejected in PEP 695 alias ───────────
# [pr_diff] (0.20): type Bad3 = Final[int] must produce invalid-type-form
echo "=== BEHAVIORAL 2: Final rejected in type alias ==="
FINAL_ERRORS=$(echo "$OUTPUT" | grep "invalid-type-form" | grep -c "Final" || true)
if [ "$FINAL_ERRORS" -ge 2 ]; then
    echo "PASS: Final flagged in PEP 695 aliases"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL: expected >=2 Final invalid-type-form errors, got $FINAL_ERRORS"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.20)")

# ── BEHAVIORAL 3 (0.10): Required/NotRequired/ReadOnly rejected ────
# [pr_diff] (0.10): Required, NotRequired, ReadOnly must produce invalid-type-form
echo "=== BEHAVIORAL 3: Required/NotRequired/ReadOnly rejected ==="
RNR_ERRORS=$(echo "$OUTPUT" | grep "invalid-type-form" | grep -cE "Required|NotRequired|ReadOnly" || true)
if [ "$RNR_ERRORS" -ge 3 ]; then
    echo "PASS: Required/NotRequired/ReadOnly flagged"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: expected >=3 Required/NotRequired/ReadOnly errors, got $RNR_ERRORS"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── BEHAVIORAL 4 (0.10): InitVar rejected in PEP 695 alias ─────────
# [pr_diff] (0.10): type Bad8 = InitVar[int] and bare InitVar must produce errors
echo "=== BEHAVIORAL 4: InitVar rejected in type alias ==="
INITVAR_ERRORS=$(echo "$OUTPUT" | grep "invalid-type-form" | grep -c "InitVar" || true)
if [ "$INITVAR_ERRORS" -ge 2 ]; then
    echo "PASS: InitVar flagged in PEP 695 aliases"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: expected >=2 InitVar invalid-type-form errors, got $INITVAR_ERRORS"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── BEHAVIORAL 5 (0.10): Total error count matches expectations ─────
# [pr_diff] (0.10): All 9 bad aliases should produce at least 9 diagnostics
echo "=== BEHAVIORAL 5: total diagnostic count ==="
TOTAL_ERRORS=$(echo "$OUTPUT" | grep -c "invalid-type-form" || true)
if [ "$TOTAL_ERRORS" -ge 9 ]; then
    echo "PASS: all 9 qualifiers flagged ($TOTAL_ERRORS diagnostics)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: expected >=9 total invalid-type-form diagnostics, got $TOTAL_ERRORS"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── PASS-TO-PASS 1 (0.10): Valid PEP 695 aliases still work ────────
# [pr_diff] (0.10): Valid type aliases must produce no errors
echo "=== PASS-TO-PASS 1: valid PEP 695 aliases ==="
OUTPUT_VALID=$("$TY" check /tmp/test_pep695_valid.py 2>&1 || true)
echo "$OUTPUT_VALID"
if echo "$OUTPUT_VALID" | grep -qi "error\|invalid"; then
    echo "FAIL: valid PEP 695 aliases produce errors"
else
    echo "PASS: valid aliases accepted"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── PASS-TO-PASS 2 (0.10): ClassVar in annotations still valid ─────
# [pr_diff] (0.10): ClassVar in class annotations must not regress
echo "=== PASS-TO-PASS 2: ClassVar in annotations still works ==="
OUTPUT_ANN=$("$TY" check /tmp/test_classvar_annotation.py 2>&1 || true)
echo "$OUTPUT_ANN"
if echo "$OUTPUT_ANN" | grep -qi "error\|invalid"; then
    echo "FAIL: ClassVar in annotations regressed"
else
    echo "PASS: ClassVar in annotations still accepted"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# ── CONFIG-DERIVED (0.05): Error messages are concise ───────────────
# [agent_config] (0.05): "error messages concise" — AGENTS.md:83 @ 6505b079
echo "=== CONFIG: error messages concise ==="
# Check that error messages fit in reasonable width (< 120 chars per line)
LONG_MSGS=$(echo "$OUTPUT" | grep "invalid-type-form" | awk 'length > 150' | wc -l)
if [ "$LONG_MSGS" -eq 0 ]; then
    echo "PASS: error messages are concise"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: some error messages exceed 150 chars"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores for reward.json
BEHAVIORAL=$(python3 -c "
b1 = min($SCORE, 0.75)
print(round(b1, 4))
")
REGRESSION=$(python3 -c "
r = min(max($SCORE - 0.75, 0), 0.20)
print(round(r, 4))
")
CONFIG=$(python3 -c "
c = min(max($SCORE - 0.95, 0), 0.05)
print(round(c, 4))
")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
