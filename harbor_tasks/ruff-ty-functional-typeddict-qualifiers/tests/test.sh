#!/usr/bin/env bash
set -euo pipefail

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

# Test 1: ReadOnly in functional TypedDict
cat > /tmp/test_readonly_functional.py <<'PYEOF'
from typing_extensions import TypedDict, ReadOnly

TD = TypedDict("TD", {"id": ReadOnly[int], "name": str})
d = TD(id=1, name="x")
d["id"] = 2     # should error: invalid-assignment (read-only key)
d["name"] = "y"  # should be fine
PYEOF

# Test 2: NotRequired in functional TypedDict (total=True default)
cat > /tmp/test_notrequired_functional.py <<'PYEOF'
from typing_extensions import TypedDict, NotRequired

TD = TypedDict("TD", {"name": str, "year": NotRequired[int]})
ok = TD(name="x")           # should be valid — year is not required
also_ok = TD(name="x", year=1)  # should be valid
PYEOF

# Test 3: Required in functional TypedDict with total=False
cat > /tmp/test_required_functional.py <<'PYEOF'
from typing_extensions import TypedDict, Required

TD = TypedDict("TD", {"name": Required[str], "year": int}, total=False)
ok = TD(name="x")           # should be valid — year is optional
bad = TD()                   # should error: missing required key "name"
bad2 = TD(year=1)            # should error: missing required key "name"
PYEOF

# Test 4: String forward reference wrapping qualifier
cat > /tmp/test_string_qualifier.py <<'PYEOF'
from typing_extensions import TypedDict, NotRequired

TD = TypedDict("TD", {"required": str, "optional": "NotRequired[int]"})
ok = TD(required="hello")   # should be valid — optional is not required
PYEOF

# Test 5: Pass-to-pass — basic functional TypedDict still works
cat > /tmp/test_functional_basic.py <<'PYEOF'
from typing_extensions import TypedDict

Movie = TypedDict("Movie", {"name": str, "year": int})
m = Movie(name="The Matrix", year=1999)
reveal_type(m)
reveal_type(m["name"])
PYEOF

# Test 6: Pass-to-pass — class-based TypedDict with qualifiers still works
cat > /tmp/test_class_qualifiers.py <<'PYEOF'
from typing_extensions import TypedDict, ReadOnly, NotRequired

class Movie(TypedDict):
    name: str
    year: NotRequired[int]
    id: ReadOnly[int]

m = Movie(name="The Matrix", id=1)
m["id"] = 2  # should error: invalid-assignment (read-only key)
PYEOF

# ── BEHAVIORAL 1 (0.20): ReadOnly enforced in functional TypedDict ──
# [pr_diff] (0.20): Assigning to ReadOnly field must produce invalid-assignment
echo "=== BEHAVIORAL 1: ReadOnly in functional TypedDict ==="
OUTPUT1=$("$TY" check /tmp/test_readonly_functional.py 2>&1 || true)
echo "$OUTPUT1"
if echo "$OUTPUT1" | grep -q "invalid-assignment"; then
    READONLY_ERRORS=$(echo "$OUTPUT1" | grep -c "invalid-assignment" || true)
    if [ "$READONLY_ERRORS" -ge 1 ]; then
        echo "PASS: ReadOnly enforced in functional TypedDict"
        BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
    else
        echo "FAIL: no invalid-assignment for ReadOnly field"
    fi
else
    echo "FAIL: no invalid-assignment diagnostic for ReadOnly field"
fi

# ── BEHAVIORAL 2 (0.20): NotRequired allows omission ────────────────
# [pr_diff] (0.20): Omitting NotRequired field must not produce missing-typed-dict-key
echo "=== BEHAVIORAL 2: NotRequired in functional TypedDict ==="
OUTPUT2=$("$TY" check /tmp/test_notrequired_functional.py 2>&1 || true)
echo "$OUTPUT2"
if echo "$OUTPUT2" | grep -q "missing-typed-dict-key"; then
    echo "FAIL: NotRequired field still treated as required"
else
    echo "PASS: NotRequired field correctly optional"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
fi

# ── BEHAVIORAL 3 (0.20): Required enforced with total=False ─────────
# [pr_diff] (0.20): Omitting Required field in total=False must produce missing-typed-dict-key
echo "=== BEHAVIORAL 3: Required in functional TypedDict (total=False) ==="
OUTPUT3=$("$TY" check /tmp/test_required_functional.py 2>&1 || true)
echo "$OUTPUT3"
REQUIRED_ERRORS=$(echo "$OUTPUT3" | grep -c "missing-typed-dict-key" || true)
if [ "$REQUIRED_ERRORS" -ge 1 ]; then
    echo "PASS: Required enforced with total=False ($REQUIRED_ERRORS errors)"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
else
    echo "FAIL: Required not enforced with total=False"
fi

# ── BEHAVIORAL 4 (0.10): String annotation with qualifier ───────────
# [pr_diff] (0.10): "NotRequired[int]" as string annotation must be respected
echo "=== BEHAVIORAL 4: String forward ref with qualifier ==="
OUTPUT4=$("$TY" check /tmp/test_string_qualifier.py 2>&1 || true)
echo "$OUTPUT4"
if echo "$OUTPUT4" | grep -q "missing-typed-dict-key"; then
    echo "FAIL: String NotRequired still treated as required"
else
    echo "PASS: String qualifier correctly handled"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.10)")
fi

# ── PASS-TO-PASS 1 (0.10): Basic functional TypedDict still works ───
# [pr_diff] (0.10): Basic functional TypedDict must not regress
echo "=== PASS-TO-PASS 1: basic functional TypedDict ==="
OUTPUT5=$("$TY" check /tmp/test_functional_basic.py 2>&1 || true)
echo "$OUTPUT5"
if echo "$OUTPUT5" | grep -qi "error"; then
    echo "FAIL: basic functional TypedDict regressed"
else
    echo "PASS: basic functional TypedDict still works"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
fi

# ── PASS-TO-PASS 2 (0.10): Class-based qualifiers still work ────────
# [pr_diff] (0.10): Class-based TypedDict with qualifiers must not regress
echo "=== PASS-TO-PASS 2: class-based TypedDict qualifiers ==="
OUTPUT6=$("$TY" check /tmp/test_class_qualifiers.py 2>&1 || true)
echo "$OUTPUT6"
if echo "$OUTPUT6" | grep -q "invalid-assignment"; then
    echo "PASS: class-based ReadOnly still enforced"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
else
    echo "FAIL: class-based ReadOnly enforcement regressed"
fi

# ── CONFIG-DERIVED (0.05): No unwrap/panic in changed files ──────────
# [agent_config] (0.05): "avoid panic!, unreachable!, .unwrap()" — AGENTS.md:79 @ 8c2a9cfb
echo "=== CONFIG: no unwrap/panic in new code ==="
DIFF_OUTPUT=$(git diff HEAD 2>/dev/null || true)
UNWRAP_COUNT=$(echo "$DIFF_OUTPUT" | grep "^+" | grep -cE '\.unwrap\(\)|panic!\(|unreachable!\(' || true)
if [ "$UNWRAP_COUNT" -eq 0 ]; then
    echo "PASS: no unwrap/panic in new code"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: found $UNWRAP_COUNT unwrap/panic calls in new code"
fi

# ── CONFIG-DERIVED (0.05): Imports at top of file ────────────────────
# [agent_config] (0.05): "Rust imports at top of file" — AGENTS.md:76 @ 8c2a9cfb
echo "=== CONFIG: imports at top of file ==="
DIFF_FILES=$(echo "$DIFF_OUTPUT" | grep "^+++ b/" | sed 's|^+++ b/||' | grep '\.rs$' || true)
LOCAL_IMPORTS=0
for f in $DIFF_FILES; do
    if [ -f "$f" ]; then
        NEW_INDENTED=$(echo "$DIFF_OUTPUT" | grep "^+    use " | wc -l || true)
        LOCAL_IMPORTS=$((LOCAL_IMPORTS + NEW_INDENTED))
    fi
done
if [ "$LOCAL_IMPORTS" -eq 0 ]; then
    echo "PASS: no local imports added"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: found $LOCAL_IMPORTS local use statements in new code"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "  behavioral=$BEHAVIORAL  regression=$REGRESSION  config=$CONFIG"
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
