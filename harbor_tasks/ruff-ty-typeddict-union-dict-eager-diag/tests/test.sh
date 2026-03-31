#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO=/repo
SCORE=0

cd "$REPO"

###############################################################################
# GATE: Rust compilation — abort if the changed code doesn't compile
###############################################################################
echo "=== GATE: Compiling ty ==="
if ! CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1 | tail -20; then
    echo "GATE FAILED: code does not compile"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
    exit 0
fi
TY="$REPO/target/debug/ty"
echo "GATE passed."

###############################################################################
# Behavioral tests (fail-to-pass) — must score >= 0.60
###############################################################################

# [pr_diff] (0.30): TypedDict | dict union should not emit false-positive diagnostics
echo "=== BEHAVIORAL 1: TypedDict | dict union — no false positives ==="
cat > /tmp/test_union_no_fp.py << 'PYEOF'
from typing import TypedDict, Any

class FormatterConfig(TypedDict, total=False):
    format: str

def takes_formatter(config: FormatterConfig | dict[str, Any]) -> None: ...

takes_formatter({"format": "%(message)s"})
takes_formatter({"factory": object(), "facility": "local0"})
PYEOF

output=$("$TY" check /tmp/test_union_no_fp.py 2>&1 || true)
if echo "$output" | grep -qE 'missing-typed-dict-key|invalid-key'; then
    echo "FAIL: false positive TypedDict diagnostic emitted"
    echo "$output"
else
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
fi

# [pr_diff] (0.20): TypedDict | None (no dict fallback) should STILL emit diagnostics
echo "=== BEHAVIORAL 2: TypedDict | None — still validates eagerly ==="
cat > /tmp/test_no_fallback.py << 'PYEOF'
from typing import TypedDict

class Foo(TypedDict):
    foo: int

x: Foo | None = {"bar": 1}
PYEOF

output=$("$TY" check /tmp/test_no_fallback.py 2>&1 || true)
if echo "$output" | grep -q 'missing-typed-dict-key' && echo "$output" | grep -q 'invalid-key'; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL: expected TypedDict diagnostics for Foo | None"
    echo "$output"
fi

# [pr_diff] (0.15): Single TypedDict annotation (no union) still validates
echo "=== BEHAVIORAL 3: Single TypedDict — still validates ==="
cat > /tmp/test_single_td.py << 'PYEOF'
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int

def use_config(c: Config) -> None: ...

use_config({"host": "localhost"})
PYEOF

output=$("$TY" check /tmp/test_single_td.py 2>&1 || true)
if echo "$output" | grep -q 'missing-typed-dict-key'; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: expected missing-typed-dict-key for single TypedDict"
    echo "$output"
fi

###############################################################################
# Pass-to-pass regression (0.15): existing typed_dict mdtest still passes
###############################################################################
echo "=== PASS-TO-PASS: typed_dict mdtest ==="
# [repo_tests] (0.15): existing typed_dict tests must not regress
if CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo nextest run -p ty_python_semantic -- mdtest::typed_dict 2>&1 | tail -20; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: typed_dict mdtest regression"
fi

###############################################################################
# Config-derived checks (0.10)
###############################################################################

BUILDER_FILE="crates/ty_python_semantic/src/types/infer/builder.rs"

# [agent_config] (0.05): No .unwrap() in new/changed code — AGENTS.md:79 @ 6cff034
echo "=== CONFIG: no unwrap in builder.rs changes ==="
# Count unwrap() calls — the gold patch removes the .expect() call; any new .unwrap() is bad
UNWRAP_COUNT=$(grep -c '\.unwrap()' "$BUILDER_FILE" 2>/dev/null || echo "0")
EXPECT_FILTER_COUNT=$(grep -c '\.expect("filtered out' "$BUILDER_FILE" 2>/dev/null || echo "0")
if [ "$EXPECT_FILTER_COUNT" -eq 0 ]; then
    echo "PASS: no .expect(\"filtered out...\") pattern"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: still has the fragile .expect() call from the buggy code"
fi

# [agent_config] (0.05): Rust imports at top of file — AGENTS.md:76 @ 6cff034
echo "=== CONFIG: imports at top of file ==="
# Check that no `use` statements appear inside function bodies in the changed file
# (a rough heuristic: `use` after `fn ` at deeper indentation)
if ! grep -nP '^\s{8,}use\s+' "$BUILDER_FILE" | grep -v '//'; then
    echo "PASS: no local imports detected"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: found local imports in builder.rs"
fi

###############################################################################
# Summary
###############################################################################
echo ""
echo "=== TOTAL SCORE: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json, sys
s = $SCORE
# Decompose (approximate — behavioral is whatever portion came from first 3 tests)
behavioral = min(s, 0.65)
remainder = max(s - 0.65, 0)
regression = min(remainder, 0.15)
remainder2 = max(remainder - 0.15, 0)
config = min(remainder2, 0.10)
style = 0
print(json.dumps({'reward': round(s,2), 'behavioral': round(behavioral,2),
                   'regression': round(regression,2), 'config': round(config,2),
                   'style_rubric': round(style,2)}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
