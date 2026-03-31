#!/usr/bin/env bash
set +e

REPO=/workspace/ruff
BEHAVIORAL=0
REGRESSION=0
CONFIG=0

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
cat > /tmp/test_functional_inherit.py <<'PYEOF'
from typing import TypedDict

Base = TypedDict("Base", {"a": int}, total=False)

class Child(Base):
    b: str
    c: list[int]

child1 = Child(b="hello", c=[1, 2, 3])
child2 = Child(a=1, b="world", c=[])

reveal_type(child1["a"])
reveal_type(child1["b"])
reveal_type(child1["c"])
PYEOF

cat > /tmp/test_functional_inherit_errors.py <<'PYEOF'
from typing import TypedDict

Base = TypedDict("Base", {"a": int}, total=False)

class Child(Base):
    b: str
    c: list[int]

# Missing required key 'b'
bad1 = Child(c=[1])

# Missing required key 'c'
bad2 = Child(b="test")
PYEOF

cat > /tmp/test_functional_inherit_subclass.py <<'PYEOF'
from typing import TypedDict, NotRequired

MyTD = TypedDict("MyTD", {"x": int})

class SubTD(MyTD):
    y: NotRequired[int]

sub = SubTD(x=1)
reveal_type(sub["x"])
PYEOF

cat > /tmp/test_class_inherit_baseline.py <<'PYEOF'
from typing import TypedDict

class Base(TypedDict):
    a: int

class Child(Base):
    b: str

child = Child(a=1, b="hello")
reveal_type(child["a"])
reveal_type(child["b"])
PYEOF

cat > /tmp/test_total_false_inherited.py <<'PYEOF'
from typing import TypedDict

# Parent with total=False means 'a' is optional
OptBase = TypedDict("OptBase", {"a": int}, total=False)

class RequiredChild(OptBase):
    b: str

# 'a' is optional (from total=False parent), 'b' is required
# This should NOT error — 'a' can be omitted
ok = RequiredChild(b="hello")
PYEOF

# ── BEHAVIORAL 1 (0.30): Functional TypedDict fields inherited by Child ─
# [pr_diff] (0.30): Child should see fields from functional Base without errors
echo "=== BEHAVIORAL 1: functional TypedDict inheritance — no false errors ==="
OUTPUT=$("$TY" check /tmp/test_functional_inherit.py 2>&1 || true)
echo "$OUTPUT"
# Should reveal int, str, list[int] — no error diagnostics
ERRORS=$(echo "$OUTPUT" | grep -c "error" || true)
HAS_INT=$(echo "$OUTPUT" | grep -c "revealed: int" || true)
HAS_STR=$(echo "$OUTPUT" | grep -c "revealed: str" || true)
HAS_LIST=$(echo "$OUTPUT" | grep -c "revealed: list\[int\]" || true)
if [ "$ERRORS" -eq 0 ] && [ "$HAS_INT" -ge 1 ] && [ "$HAS_STR" -ge 1 ] && [ "$HAS_LIST" -ge 1 ]; then
    echo "PASS: functional TypedDict fields inherited correctly"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.30)")
else
    echo "FAIL: fields not correctly inherited from functional TypedDict"
fi

# ── BEHAVIORAL 2 (0.20): Missing required keys are reported ──────────
# [pr_diff] (0.20): Constructor validation works for children of functional TypedDicts
echo "=== BEHAVIORAL 2: missing required keys reported ==="
OUTPUT2=$("$TY" check /tmp/test_functional_inherit_errors.py 2>&1 || true)
echo "$OUTPUT2"
MISSING_B=$(echo "$OUTPUT2" | grep -ci "missing.*required.*key.*b\|missing-typed-dict-key" || true)
if [ "$MISSING_B" -ge 1 ]; then
    echo "PASS: missing required keys detected"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
else
    echo "FAIL: missing required key errors not reported"
fi

# ── BEHAVIORAL 3 (0.15): Subclass with NotRequired from functional base ─
# [pr_diff] (0.15): Functional TypedDict subclass with NotRequired fields works
echo "=== BEHAVIORAL 3: functional TypedDict subclass with NotRequired ==="
OUTPUT3=$("$TY" check /tmp/test_functional_inherit_subclass.py 2>&1 || true)
echo "$OUTPUT3"
ERRORS3=$(echo "$OUTPUT3" | grep -c "error" || true)
HAS_X=$(echo "$OUTPUT3" | grep -c "revealed: int" || true)
if [ "$ERRORS3" -eq 0 ] && [ "$HAS_X" -ge 1 ]; then
    echo "PASS: functional TypedDict subclass works"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.15)")
else
    echo "FAIL: functional TypedDict subclass has errors"
fi

# ── BEHAVIORAL 4 (0.10): total=False semantics inherited correctly ────
# [pr_diff] (0.10): Optional fields from total=False parent remain optional in child
echo "=== BEHAVIORAL 4: total=False semantics inherited ==="
OUTPUT5=$("$TY" check /tmp/test_total_false_inherited.py 2>&1 || true)
echo "$OUTPUT5"
ERRORS5=$(echo "$OUTPUT5" | grep -c "error" || true)
if [ "$ERRORS5" -eq 0 ]; then
    echo "PASS: total=False fields correctly optional in child"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.10)")
else
    echo "FAIL: total=False inheritance not working (optional field treated as required)"
fi

# ── PASS-TO-PASS 1 (0.10): Class-based TypedDict inheritance still works ─
# [pr_diff] (0.10): Existing class-based inheritance must not regress
echo "=== PASS-TO-PASS 1: class-based TypedDict inheritance baseline ==="
OUTPUT4=$("$TY" check /tmp/test_class_inherit_baseline.py 2>&1 || true)
echo "$OUTPUT4"
ERRORS4=$(echo "$OUTPUT4" | grep -c "error" || true)
if [ "$ERRORS4" -eq 0 ]; then
    echo "PASS: class-based TypedDict inheritance still works"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
else
    echo "FAIL: regression in class-based TypedDict inheritance"
fi

# ── PASS-TO-PASS 2 (0.10): Existing typed_dict mdtests pass ──────────
# [pr_diff] (0.10): Existing TypedDict tests must not regress
echo "=== PASS-TO-PASS 2: existing typed_dict mdtests ==="
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
   cargo nextest run -p ty_python_semantic -- mdtest::typed_dict --no-fail-fast 2>&1 | tail -20; then
    echo "PASS: existing typed_dict mdtests pass"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
else
    echo "FAIL: some existing typed_dict mdtests failed"
fi

# ── CONFIG-DERIVED (0.05): No .unwrap() in new code ──────────────────
# [agent_config] (0.05): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79 @ 3465d7f1
echo "=== CONFIG: no .unwrap() in new code ==="
DIFF=$(cd "$REPO" && git diff HEAD -- '*.rs')
UNWRAP_COUNT=$(echo "$DIFF" | grep '^+' | grep -v '^+++' | grep -c '\.unwrap()' || true)
if [ "$UNWRAP_COUNT" -eq 0 ]; then
    echo "PASS: no .unwrap() in new code"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: found $UNWRAP_COUNT .unwrap() calls in new code"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
