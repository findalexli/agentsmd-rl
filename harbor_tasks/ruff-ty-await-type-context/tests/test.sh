#!/usr/bin/env bash
set +e

REPO=/workspace/ruff
BEHAVIORAL=0
REGRESSION=0
CONFIG=0

cd "$REPO"

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

cat > /tmp/test_await_literal.py <<'PYEOF'
from typing import Literal

async def make_lst[T](x: T) -> list[T]:
    return [x]

async def _():
    x: list[Literal[1]] = await make_lst(1)
PYEOF

cat > /tmp/test_await_self.py <<'PYEOF'
from typing import Self

class Parent:
    async def get_list(self) -> list[Self]:
        return [self]

    async def test(self):
        my_list: list[Parent] = await self.get_list()

class Child(Parent):
    async def func2(self):
        childs: list[Child] = await self.get_list()
PYEOF

cat > /tmp/test_await_union.py <<'PYEOF'
async def make_lst[T](x: T) -> list[T]:
    return [x]

async def _():
    x: list[int | None] = await make_lst(1)
PYEOF

cat > /tmp/test_await_true_positive.py <<'PYEOF'
async def get_int() -> int:
    return 42

async def _():
    x: str = await get_int()
PYEOF

cat > /tmp/test_await_basic.py <<'PYEOF'
async def identity[T](x: T) -> T:
    return x

async def _():
    y: int = await identity(42)
PYEOF

cat > /tmp/test_await_nocontext.py <<'PYEOF'
async def make_lst[T](x: T) -> list[T]:
    return [x]

async def _():
    x = await make_lst(1)
PYEOF

# ── BEHAVIORAL 1 (0.25): Literal type context propagates through await ─
# [pr_diff] (0.25): list[Literal[1]] annotation should satisfy via type context
echo "=== BEHAVIORAL 1: Literal type context through await ==="
OUTPUT=$("$TY" check /tmp/test_await_literal.py 2>&1 || true)
echo "$OUTPUT"
if echo "$OUTPUT" | grep -qi "invalid-assignment"; then
    echo "FAIL: false positive diagnostic on await with Literal type context"
else
    echo "PASS: no false positive with Literal type context"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.25)")
fi

# ── BEHAVIORAL 2 (0.25): Self type context propagates through await ────
# [pr_diff] (0.25): list[Self] annotation should satisfy via type context
echo "=== BEHAVIORAL 2: Self type context through await ==="
OUTPUT2=$("$TY" check /tmp/test_await_self.py 2>&1 || true)
echo "$OUTPUT2"
if echo "$OUTPUT2" | grep -qi "invalid-assignment"; then
    echo "FAIL: false positive diagnostic on await with Self type context"
else
    echo "PASS: no false positive with Self type context"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.25)")
fi

# ── BEHAVIORAL 3 (0.10): True positive — genuine type error still caught ─
# [pr_diff] (0.10): Non-generic await type mismatch must still produce error
echo "=== BEHAVIORAL 3: True positive — genuine error still detected ==="
OUTPUT_TP=$("$TY" check /tmp/test_await_true_positive.py 2>&1 || true)
echo "$OUTPUT_TP"
if echo "$OUTPUT_TP" | grep -qi "invalid-assignment"; then
    echo "PASS: genuine type error through await still caught"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.10)")
else
    echo "FAIL: genuine type error not detected — possible over-suppression or Unknown return"
fi

# ── BEHAVIORAL 4 (0.05): Union type context propagates through await ────
# [pr_diff] (0.05): list[int | None] annotation should satisfy via type context
echo "=== BEHAVIORAL 4: Union type context through await ==="
OUTPUT_UN=$("$TY" check /tmp/test_await_union.py 2>&1 || true)
echo "$OUTPUT_UN"
if echo "$OUTPUT_UN" | grep -qi "invalid-assignment"; then
    echo "FAIL: false positive diagnostic on await with union type context"
else
    echo "PASS: no false positive with union type context"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.05)")
fi

# ── PASS-TO-PASS 1 (0.10): Basic typed await still works ──────────────
# [pr_diff] (0.10): Typed await should continue to work without false errors
echo "=== PASS-TO-PASS 1: basic typed await ==="
OUTPUT3=$("$TY" check /tmp/test_await_basic.py 2>&1 || true)
echo "$OUTPUT3"
if echo "$OUTPUT3" | grep -qi "invalid-assignment"; then
    echo "FAIL: regression on basic typed await"
else
    echo "PASS: basic typed await still works"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
fi

# ── PASS-TO-PASS 2 (0.10): Await without annotation infers correctly ──
# [pr_diff] (0.10): Bare await (no annotation) should still infer correctly
echo "=== PASS-TO-PASS 2: await without type annotation ==="
OUTPUT4=$("$TY" check /tmp/test_await_nocontext.py 2>&1 || true)
echo "$OUTPUT4"
if echo "$OUTPUT4" | grep -qi "invalid-assignment"; then
    echo "FAIL: regression on await without annotation"
else
    echo "PASS: await without annotation infers correctly"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
fi

# ── CONFIG-DERIVED (0.05): infer_await_expression signature takes tcx ───
# [agent_config] (0.05): "Avoid writing significant amounts of new code" — AGENTS.md:78 @ f283ddc3
echo "=== CONFIG: minimal change — tcx param added to infer_await_expression ==="
DIFF=$(git diff HEAD -- crates/ty_python_semantic/src/types/infer/builder.rs)
if echo "$DIFF" | grep -q '+.*infer_await_expression.*tcx\|+.*TypeContext'; then
    echo "PASS: infer_await_expression takes type context parameter"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: infer_await_expression signature not updated with type context"
fi

# ── ANTI-STUB (0.05): builder.rs was actually modified ──────────────
# [pr_diff] (0.05): Actual code change in builder.rs, not a stub
echo "=== ANTI-STUB: builder.rs modified ==="
DIFF2=$(git diff HEAD -- crates/ty_python_semantic/src/types/infer/builder.rs)
if [ -n "$DIFF2" ] && echo "$DIFF2" | grep -q '+.*Awaitable\|+.*infer_expression.*value\|+.*tcx'; then
    echo "PASS: builder.rs has substantive changes"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: builder.rs not modified or changes are stubs"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
