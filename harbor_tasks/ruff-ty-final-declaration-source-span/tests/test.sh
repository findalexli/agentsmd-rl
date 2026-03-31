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

# Test 1: Class-body Final with value, assignment in method
cat > /tmp/test_final_method.py <<'PYEOF'
from typing import Final

class C:
    x: Final[int] = 1

    def f(self):
        self.x = 2
PYEOF

# Test 2: __init__ assignment after class-body Final value
cat > /tmp/test_final_init.py <<'PYEOF'
from typing import Final

class C:
    x: Final[int] = 1

    def __init__(self):
        self.x = 2
PYEOF

# Test 3: Inherited Final attribute from parent class
cat > /tmp/test_final_inherited.py <<'PYEOF'
from typing import Final

class Base:
    x: Final[int] = 1

class Child(Base):
    def f(self):
        self.x = 2
PYEOF

# Test 4: Module-level Final without value (pass-to-pass)
cat > /tmp/test_final_module.py <<'PYEOF'
from typing import Final

UNINITIALIZED: Final[int]
INITIALIZED: Final[int] = 42
PYEOF

# ── BEHAVIORAL 1 (0.25): Method assignment shows Final source annotation ──
# [pr_diff] (0.25): Diagnostic for method assignment must show "Attribute declared as `Final` here"
echo "=== BEHAVIORAL 1: Method assignment shows Final source annotation ==="
OUTPUT=$("$TY" check /tmp/test_final_method.py 2>&1 || true)
echo "$OUTPUT"
if echo "$OUTPUT" | grep -q 'invalid-assignment' && echo "$OUTPUT" | grep -qi 'declared as.*Final.*here\|Final.*declared.*here'; then
    echo "PASS: diagnostic includes Final declaration annotation"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.25)")
else
    echo "FAIL: diagnostic missing Final declaration annotation"
fi

# ── BEHAVIORAL 2 (0.20): __init__ reassignment shows annotation + "already has a value" ──
# [pr_diff] (0.20): __init__ assignment after class-body value shows Final source
echo "=== BEHAVIORAL 2: __init__ reassignment shows Final source annotation ==="
OUTPUT2=$("$TY" check /tmp/test_final_init.py 2>&1 || true)
echo "$OUTPUT2"
if echo "$OUTPUT2" | grep -q 'invalid-assignment' \
   && echo "$OUTPUT2" | grep -q 'already has a value' \
   && echo "$OUTPUT2" | grep -qi 'declared as.*Final.*here\|Final.*declared.*here'; then
    echo "PASS: __init__ reassignment diagnostic has Final source annotation"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
else
    echo "FAIL: __init__ reassignment diagnostic missing annotation"
fi

# ── BEHAVIORAL 3 (0.20): Inherited Final attribute shows annotation from parent ──
# [pr_diff] (0.20): Inherited Final attribute assignment shows declaration site from base class
echo "=== BEHAVIORAL 3: Inherited Final shows annotation from parent ==="
OUTPUT3=$("$TY" check /tmp/test_final_inherited.py 2>&1 || true)
echo "$OUTPUT3"
if echo "$OUTPUT3" | grep -q 'invalid-assignment' && echo "$OUTPUT3" | grep -qi 'declared as.*Final.*here\|Final.*declared.*here'; then
    echo "PASS: inherited Final diagnostic includes declaration annotation"
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.20)")
else
    echo "FAIL: inherited Final diagnostic missing declaration annotation"
fi

# ── PASS-TO-PASS 1 (0.10): Module-level Final without value still diagnosed ──
# [pr_diff] (0.10): final-without-value diagnostic must not regress
echo "=== PASS-TO-PASS 1: Module-level Final without value ==="
OUTPUT4=$("$TY" check /tmp/test_final_module.py 2>&1 || true)
echo "$OUTPUT4"
if echo "$OUTPUT4" | grep -q 'final-without-value'; then
    echo "PASS: final-without-value still reported"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
else
    echo "FAIL: final-without-value not reported"
fi

# ── PASS-TO-PASS 2 (0.05): Basic invalid-assignment still works for method ──
# [pr_diff] (0.05): invalid-assignment error text must still appear
echo "=== PASS-TO-PASS 2: Basic invalid-assignment message ==="
if echo "$OUTPUT" | grep -q 'Final.*attributes can only be assigned'; then
    echo "PASS: invalid-assignment primary message intact"
    REGRESSION=$(python3 -c "print($REGRESSION + 0.05)")
else
    echo "FAIL: invalid-assignment primary message missing"
fi

# ── CONFIG-DERIVED (0.10): Rust imports at top + no new .unwrap() ──
FA_FILE="crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs"
TYPES_FILE="crates/ty_python_semantic/src/types.rs"

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ 929eb523
echo "=== CONFIG: Rust imports at top ==="
IMPORT_OK=true
for F in "$FA_FILE" "$TYPES_FILE"; do
    FPATH="$REPO/$F"
    if [ -f "$FPATH" ]; then
        if python3 -c "
import re
content = open('$FPATH').read()
in_fn = False
brace_depth = 0
for line in content.splitlines():
    stripped = line.strip()
    if re.match(r'(pub\s+)?(fn|async\s+fn)\s+', stripped):
        in_fn = True
        brace_depth = 0
    if in_fn:
        brace_depth += stripped.count('{') - stripped.count('}')
        if brace_depth > 0 and re.match(r'use\s+', stripped):
            exit(1)
        if brace_depth <= 0 and '{' in line:
            in_fn = False
"; then
            :
        else
            IMPORT_OK=false
            echo "FAIL: found import inside function body in $F"
        fi
    fi
done
if $IMPORT_OK; then
    echo "PASS: imports at file top"
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
fi

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 929eb523
echo "=== CONFIG: No new .unwrap() calls ==="
if [ -f "$REPO/$FA_FILE" ]; then
    BASE_UNWRAPS=$(cd "$REPO" && git show HEAD:"$FA_FILE" 2>/dev/null | grep -c '\.unwrap()' || echo "0")
    CURR_UNWRAPS=$(grep -c '\.unwrap()' "$REPO/$FA_FILE" || echo "0")
    if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
        echo "PASS: no new .unwrap() calls ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
        CONFIG=$(python3 -c "print($CONFIG + 0.05)")
    else
        echo "FAIL: new .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
    fi
else
    echo "FAIL: $FA_FILE not found"
fi

# ── ANTI-STUB (0.10): final_attribute.rs has meaningful code additions ─────
# [pr_diff] (0.10): final_attribute.rs must have substantive non-comment code additions
echo "=== ANTI-STUB: final_attribute.rs meaningful additions ==="
if [ -f "$REPO/$FA_FILE" ]; then
    # Count only added lines (^+), excluding diff header (^+++), blank lines, and comments
    ADDED_CODE_LINES=$(cd "$REPO" && git diff HEAD -- "$FA_FILE" \
        | grep '^+[^+]' \
        | grep -v '^\+\s*$' \
        | grep -v '^\+\s*//' \
        | grep -v '^\+\s*\*' \
        | wc -l)
    if [ "$ADDED_CODE_LINES" -ge 8 ]; then
        echo "PASS: $ADDED_CODE_LINES meaningful added code lines"
        REGRESSION=$(python3 -c "print($REGRESSION + 0.10)")
    else
        echo "FAIL: only $ADDED_CODE_LINES meaningful added code lines (need >=8)"
    fi
else
    echo "FAIL: $FA_FILE not found"
fi

# ── Compute final reward ────────────────────────────────────────────
REWARD=$(python3 -c "print(round($BEHAVIORAL + $REGRESSION + $CONFIG, 4))")
echo ""
echo "=== FINAL SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
