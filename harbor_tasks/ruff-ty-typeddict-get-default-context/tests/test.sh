#!/usr/bin/env bash
set +e

SCORE=0
REPO=/workspace/ruff

# ── GATE (0.00): Rust compilation check ────────────────────────────
# [pr_diff] (0.00): Code must compile
echo "=== GATE: cargo check ==="
cd "$REPO"
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

# Core repro: non-required field .get() with dict literal default
cat > /tmp/test_get_context.py <<'PYEOF'
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def _(payload: Payload) -> None:
    result = payload.get("resolved", {})
    takes_resolved(result)
PYEOF

# Union of TypedDicts with same non-required field
cat > /tmp/test_get_union.py <<'PYEOF'
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

class Payload2(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def _(payload: Payload | Payload2) -> None:
    result = payload.get("resolved", {})
    takes_resolved(result)
PYEOF

# Negative test: wrong default type SHOULD still produce an error
cat > /tmp/test_get_wrong_default.py <<'PYEOF'
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def _(payload: Payload) -> None:
    result = payload.get("resolved", 42)
    takes_resolved(result)  # error: int is not ResolvedData
PYEOF

# Negative test 2: wrong type assignment from .get() with incompatible default
cat > /tmp/test_get_wrong_assign.py <<'PYEOF'
from typing import TypedDict

class Data(TypedDict, total=False):
    x: int

def _(d: Data) -> None:
    val: str = d.get("x", 0)  # error: int is not str
PYEOF

# Pass-to-pass: required field .get() with default still works
cat > /tmp/test_get_required.py <<'PYEOF'
from typing import TypedDict

class Person(TypedDict):
    name: str
    age: int

def _(p: Person) -> None:
    val: str | int = p.get("name", 0)
PYEOF

# Pass-to-pass: non-required field .get() without default returns Optional
cat > /tmp/test_get_no_default.py <<'PYEOF'
from typing import TypedDict

class Data(TypedDict, total=False):
    x: int

def _(d: Data) -> None:
    val: int | None = d.get("x")
PYEOF

# ── BEHAVIORAL 1 (0.25): Non-required field .get() with dict default ──
# [pr_diff] (0.25): payload.get("resolved", {}) should type as ResolvedData, not union
echo "=== BEHAVIORAL 1: Non-required field .get() with dict literal default ==="
OUTPUT=$("$TY" check /tmp/test_get_context.py 2>&1 || true)
echo "$OUTPUT"
if echo "$OUTPUT" | grep -qi "invalid-argument\|invalid-assignment\|error"; then
    echo "FAIL: false positive on .get() with dict default for non-required field"
else
    echo "PASS: .get() with dict default correctly infers field type"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi

# ── BEHAVIORAL 2 (0.25): Union TypedDict .get() with dict default ────
# [pr_diff] (0.25): union payload.get("resolved", {}) should also type correctly
echo "=== BEHAVIORAL 2: Union TypedDict .get() with dict default ==="
OUTPUT2=$("$TY" check /tmp/test_get_union.py 2>&1 || true)
echo "$OUTPUT2"
if echo "$OUTPUT2" | grep -qi "invalid-argument\|invalid-assignment\|error"; then
    echo "FAIL: false positive on union TypedDict .get() with dict default"
else
    echo "PASS: union TypedDict .get() with dict default works"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi

# ── BEHAVIORAL 3 (0.15): Wrong default type still produces error ─────
# [pr_diff] (0.15): payload.get("resolved", 42) should still error — proves checking isn't disabled
echo "=== BEHAVIORAL 3: Wrong default type still errors ==="
OUTPUT3=$("$TY" check /tmp/test_get_wrong_default.py 2>&1 || true)
echo "$OUTPUT3"
if echo "$OUTPUT3" | grep -qi "invalid-argument\|invalid-assignment\|error"; then
    echo "PASS: wrong default type correctly errors"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: wrong default type should produce an error but didn't"
fi

# ── BEHAVIORAL 4 (0.10): Wrong type assignment still errors ──────────
# [pr_diff] (0.10): d.get("x", 0) assigned to str should error
echo "=== BEHAVIORAL 4: Wrong type assignment still errors ==="
OUTPUT4=$("$TY" check /tmp/test_get_wrong_assign.py 2>&1 || true)
echo "$OUTPUT4"
if echo "$OUTPUT4" | grep -qi "invalid-assignment\|error"; then
    echo "PASS: wrong type assignment correctly errors"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: wrong type assignment should produce an error but didn't"
fi

# ── PASS-TO-PASS 1 (0.05): Required field .get() with default still works ──
# [pr_diff] (0.05): Required field .get() with non-matching default must not regress
echo "=== PASS-TO-PASS 1: Required field .get() with default ==="
OUTPUT5=$("$TY" check /tmp/test_get_required.py 2>&1 || true)
echo "$OUTPUT5"
if echo "$OUTPUT5" | grep -qi "invalid-assignment\|error"; then
    echo "FAIL: regression on required field .get()"
else
    echo "PASS: required field .get() still works"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── PASS-TO-PASS 2 (0.05): Non-required .get() without default still Optional ──
# [pr_diff] (0.05): .get() without default on non-required field must still be Optional
echo "=== PASS-TO-PASS 2: Non-required .get() without default ==="
OUTPUT6=$("$TY" check /tmp/test_get_no_default.py 2>&1 || true)
echo "$OUTPUT6"
if echo "$OUTPUT6" | grep -qi "invalid-assignment\|error"; then
    echo "FAIL: regression on .get() without default"
else
    echo "PASS: .get() without default still returns Optional"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

# ── CONFIG (0.05): No new .unwrap() calls ─────────────────────────────
# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ c37535dd
echo "=== CONFIG: No new .unwrap() calls ==="
TD_FILE="crates/ty_python_semantic/src/types/class/typed_dict.rs"
if [ -f "$REPO/$TD_FILE" ]; then
    BASE_UNWRAPS=$(cd "$REPO" && git show HEAD:"$TD_FILE" 2>/dev/null | grep -c '\.unwrap()' || echo "0")
    CURR_UNWRAPS=$(grep -c '\.unwrap()' "$REPO/$TD_FILE" || echo "0")
    if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
        echo "PASS: no new .unwrap() calls ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
        SCORE=$(python3 -c "print($SCORE + 0.05)")
    else
        echo "FAIL: new .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
    fi
else
    echo "SKIP: $TD_FILE not found (fix may be in different file)"
fi

# ── ANTI-STUB (0.10): typed_dict.rs has substantive changes ──────────
# [pr_diff] (0.10): Repo must have meaningful changes in the semantic analysis layer
echo "=== ANTI-STUB: substantive changes in semantic layer ==="
DIFF=$(cd "$REPO" && git diff HEAD -- 'crates/ty_python_semantic/' 2>/dev/null)
if [ -n "$DIFF" ]; then
    # Count meaningful added/changed lines (not just comments or whitespace)
    MEANINGFUL=$(echo "$DIFF" | grep '^+' | grep -v '^+++' | grep -v '^\+\s*$' | grep -v '^\+\s*//' | wc -l)
    if [ "$MEANINGFUL" -ge 5 ]; then
        echo "PASS: $MEANINGFUL meaningful lines changed in ty_python_semantic"
        SCORE=$(python3 -c "print($SCORE + 0.10)")
    else
        echo "FAIL: only $MEANINGFUL meaningful lines changed (need >=5)"
    fi
else
    echo "FAIL: no changes in crates/ty_python_semantic/"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Compute component scores
B_SCORE=$(python3 -c "print(round(min($SCORE, 0.75), 4))")
R_SCORE=$(python3 -c "s=$SCORE; print(round(min(max(s - 0.75, 0), 0.10), 4))")
C_SCORE=$(python3 -c "s=$SCORE; print(round(min(max(s - 0.85, 0), 0.05), 4))")

echo "{\"reward\": $REWARD, \"behavioral\": $B_SCORE, \"regression\": $R_SCORE, \"config\": $C_SCORE, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
