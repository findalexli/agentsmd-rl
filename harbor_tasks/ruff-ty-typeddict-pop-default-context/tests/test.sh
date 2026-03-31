#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
PASS=0.0
GATE_PASS=true

cd /workspace/ruff

##############################################################################
# GATE: Core source files exist
##############################################################################
# [pr_diff] (gate): typed_dict.rs must exist
TYPED_DICT_FILE="crates/ty_python_semantic/src/types/class/typed_dict.rs"
if [ ! -f "$TYPED_DICT_FILE" ]; then
    echo "GATE FAIL: $TYPED_DICT_FILE does not exist"
    GATE_PASS=false
fi

MDTEST_FILE="crates/ty_python_semantic/resources/mdtest/typed_dict.md"
if [ ! -f "$MDTEST_FILE" ]; then
    echo "GATE FAIL: $MDTEST_FILE does not exist"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: source file checks passed"

##############################################################################
# GATE: Code must compile (no points, but abort if it doesn't)
##############################################################################

# [pr_diff] (gate): cargo check must pass to proceed
echo "Running cargo check -p ty_python_semantic..."
if ! cargo check -p ty_python_semantic 2>&1; then
    echo "GATE FAIL: cargo check -p ty_python_semantic failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: cargo check passed"

# Build ty binary for behavioral testing
echo "Building ty binary..."
cargo build --bin ty 2>&1 || true
TY_BIN="./target/debug/ty"
if [ ! -x "$TY_BIN" ]; then
    echo "WARN: Could not build ty binary, behavioral tests will fail"
    TY_BIN=""
fi

##############################################################################
# Fail-to-pass: Behavioral tests (0.70 total)
# These MUST fail on the buggy base commit and pass on a correct fix.
##############################################################################

mkdir -p /tmp/ty_test

# --- Test 1: Core bug — pop() with empty dict default ---
cat > /tmp/ty_test/test_pop_empty_dict.py <<'PYEOF'
from typing import TypedDict

class Config(TypedDict, total=False):
    data: dict[str, int]

def f(c: Config) -> None:
    result = c.pop("data", {})
    reveal_type(result)
PYEOF

# --- Test 2: Core bug — pop() with non-empty dict default ---
cat > /tmp/ty_test/test_pop_nonempty_default.py <<'PYEOF'
from typing import TypedDict

class Config(TypedDict, total=False):
    data: dict[str, int]

def f(c: Config) -> None:
    result = c.pop("data", {"a": 1})
    reveal_type(result)
PYEOF

# --- Test 3: Core bug — pop() with list field default ---
cat > /tmp/ty_test/test_pop_list_default.py <<'PYEOF'
from typing import TypedDict

class Config(TypedDict, total=False):
    items: list[int]

def f(c: Config) -> None:
    result = c.pop("items", [])
    reveal_type(result)
PYEOF

# --- Test 4: Core bug — pop() with default on second optional field ---
cat > /tmp/ty_test/test_pop_multi_field.py <<'PYEOF'
from typing import TypedDict

class Settings(TypedDict, total=False):
    name: str
    tags: set[str]

def f(s: Settings) -> None:
    result = s.pop("tags", set())
    reveal_type(result)
PYEOF

if [ -n "$TY_BIN" ]; then
    # [pr_diff] (0.25): pop() with empty dict default infers field type
    # Buggy: reveals dict[str, int] | dict[Unknown, Unknown] (union with generic)
    # Fixed: reveals dict[str, int]
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_pop_empty_dict.py 2>&1 || true)
    echo "  ty output (pop empty dict): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*dict\[str, int\]' && \
       ! echo "$OUTPUT" | grep -qi 'revealed type.*|'; then
        PASS=$(echo "$PASS + 0.25" | bc)
        echo "PASS [0.25]: pop({}) correctly infers dict[str, int]"
    else
        echo "FAIL [0.25]: pop({}) does not correctly infer dict[str, int]"
    fi
    TOTAL=$(echo "$TOTAL + 0.25" | bc)

    # [pr_diff] (0.20): pop() with non-empty dict default infers field type
    # Buggy: may infer union; Fixed: dict[str, int]
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_pop_nonempty_default.py 2>&1 || true)
    echo "  ty output (pop nonempty default): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*dict\[str, int\]' && \
       ! echo "$OUTPUT" | grep -qi 'revealed type.*|'; then
        PASS=$(echo "$PASS + 0.20" | bc)
        echo "PASS [0.20]: pop({'a': 1}) correctly infers dict[str, int]"
    else
        echo "FAIL [0.20]: pop({'a': 1}) does not correctly infer dict[str, int]"
    fi
    TOTAL=$(echo "$TOTAL + 0.20" | bc)

    # [pr_diff] (0.15): pop() with empty list default infers list[int]
    # Buggy: reveals list[int] | list[Unknown]; Fixed: list[int]
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_pop_list_default.py 2>&1 || true)
    echo "  ty output (pop list default): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*list\[int\]' && \
       ! echo "$OUTPUT" | grep -qi 'revealed type.*|'; then
        PASS=$(echo "$PASS + 0.15" | bc)
        echo "PASS [0.15]: pop([]) correctly infers list[int]"
    else
        echo "FAIL [0.15]: pop([]) does not correctly infer list[int]"
    fi
    TOTAL=$(echo "$TOTAL + 0.15" | bc)

    # [pr_diff] (0.10): pop() with set default on a different field infers set[str]
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_pop_multi_field.py 2>&1 || true)
    echo "  ty output (pop set default): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*set\[str\]' && \
       ! echo "$OUTPUT" | grep -qi 'revealed type.*|'; then
        PASS=$(echo "$PASS + 0.10" | bc)
        echo "PASS [0.10]: pop(set()) correctly infers set[str]"
    else
        echo "FAIL [0.10]: pop(set()) does not correctly infer set[str]"
    fi
    TOTAL=$(echo "$TOTAL + 0.10" | bc)
else
    TOTAL=$(echo "$TOTAL + 0.70" | bc)
    echo "SKIP [0.70]: Could not build ty binary for behavioral tests"
fi

##############################################################################
# Pass-to-pass: Regression tests (0.20 total)
# These pass on both buggy and fixed code — verify nothing is broken.
##############################################################################

# --- P2P Test: pop() without default still works ---
cat > /tmp/ty_test/test_pop_no_default.py <<'PYEOF'
from typing import TypedDict

class Config(TypedDict, total=False):
    data: dict[str, int]

def f(c: Config) -> None:
    result = c.pop("data")
    reveal_type(result)
PYEOF

# --- P2P Test: get() bidirectional still works ---
cat > /tmp/ty_test/test_get_bidirectional.py <<'PYEOF'
from typing import TypedDict

class Config(TypedDict, total=False):
    data: dict[str, int]

def f(c: Config) -> None:
    result = c.get("data", {})
    reveal_type(result)
PYEOF

if [ -n "$TY_BIN" ]; then
    # [pr_diff] (0.05): pop() without default still works
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_pop_no_default.py 2>&1 || true)
    echo "  ty output (pop no default): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*dict\[str, int\]'; then
        PASS=$(echo "$PASS + 0.05" | bc)
        echo "PASS [0.05]: pop() without default still reveals field type"
    else
        echo "FAIL [0.05]: pop() without default broken"
    fi
    TOTAL=$(echo "$TOTAL + 0.05" | bc)

    # [pr_diff] (0.05): get() bidirectional context not regressed
    OUTPUT=$($TY_BIN check /tmp/ty_test/test_get_bidirectional.py 2>&1 || true)
    echo "  ty output (get bidirectional): $OUTPUT"
    if echo "$OUTPUT" | grep -q 'revealed type.*dict\[str, int\]' && \
       ! echo "$OUTPUT" | grep -qi 'revealed type.*|'; then
        PASS=$(echo "$PASS + 0.05" | bc)
        echo "PASS [0.05]: get() bidirectional context still works"
    else
        echo "FAIL [0.05]: get() bidirectional context broken"
    fi
    TOTAL=$(echo "$TOTAL + 0.05" | bc)
else
    TOTAL=$(echo "$TOTAL + 0.10" | bc)
    echo "SKIP [0.10]: Could not build ty binary for P2P tests"
fi

# [pr_diff] (0.10): Existing typed_dict mdtest suite still passes
echo "Running existing typed_dict mdtests..."
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
   cargo nextest run -p ty_python_semantic -- mdtest::typed_dict 2>&1 | tail -10; then
    PASS=$(echo "$PASS + 0.10" | bc)
    echo "PASS [0.10]: Existing typed_dict mdtests pass"
else
    echo "FAIL [0.10]: Existing typed_dict mdtests broke"
fi
TOTAL=$(echo "$TOTAL + 0.10" | bc)

##############################################################################
# Config-derived checks (0.05 total)
##############################################################################

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 55177205
BASE_UNWRAPS=$(git show HEAD:crates/ty_python_semantic/src/types/class/typed_dict.rs 2>/dev/null | grep -c '\.unwrap()' || echo "0")
CURR_UNWRAPS=$(grep -c '\.unwrap()' "$TYPED_DICT_FILE" || echo "0")
if [ "$CURR_UNWRAPS" -le "$BASE_UNWRAPS" ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: no new .unwrap() calls added"
else
    echo "FAIL [0.05]: new .unwrap() calls added ($BASE_UNWRAPS -> $CURR_UNWRAPS)"
fi
TOTAL=$(echo "$TOTAL + 0.05" | bc)

##############################################################################
# Anti-stub / structural (0.05 total)
##############################################################################

# [pr_diff] (0.05): typed_dict.rs not truncated
LINE_COUNT=$(wc -l < "$TYPED_DICT_FILE")
if [ "$LINE_COUNT" -gt 200 ]; then
    PASS=$(echo "$PASS + 0.05" | bc)
    echo "PASS [0.05]: $TYPED_DICT_FILE has $LINE_COUNT lines (not truncated)"
else
    echo "FAIL [0.05]: $TYPED_DICT_FILE only has $LINE_COUNT lines (likely truncated)"
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
behavioral = round(min(0.70, $PASS), 4)
regression = round(min(0.20, max(0, $PASS - 0.70)), 4)
config = round(min(0.05, max(0, $PASS - 0.90)), 4)
structural = round(min(0.05, max(0, $PASS - 0.95)), 4)
# Weights: F2P behavioral=0.70, P2P regression=0.20, config=0.05, structural=0.05
print(json.dumps({'reward': reward, 'behavioral': behavioral, 'regression': regression, 'config': config, 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
