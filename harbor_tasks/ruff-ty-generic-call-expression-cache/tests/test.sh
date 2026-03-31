#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
SCORE=0.0
DETAILS=""

add() {
    local weight=$1 earned=$2 tag="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    SCORE=$(python3 -c "print($SCORE + $earned)")
    DETAILS="${DETAILS}${tag}: earned ${earned}/${weight}\n"
}

cd /repo

# ── GATE: Syntax check — does the modified file compile? ──
# [pr_diff] (gate): Modified builder.rs must compile
echo "=== GATE: Compilation check ==="
if ! CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1; then
    echo "GATE FAILED: Code does not compile."
    echo "0.0" > /logs/verifier/reward.txt
    printf '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}\n' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: Compilation successful."

# ── Fail-to-pass: Nested generic calls complete in reasonable time ──
# [pr_diff] (0.35): Nested OrderedDict calls (6 levels) must complete within 30s
echo ""
echo "=== BEHAVIORAL: Nested OrderedDict timing (6 levels) ==="
cat > /tmp/test_nested_generic.py <<'PYEOF'
from collections import OrderedDict
OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(("one", 1)))))))
PYEOF

START=$(date +%s%N)
if timeout 30 cargo run --bin ty -- check /tmp/test_nested_generic.py 2>&1; then
    ELAPSED_MS=$(( ($(date +%s%N) - START) / 1000000 ))
    echo "Completed in ${ELAPSED_MS}ms"
    if [ "$ELAPSED_MS" -lt 30000 ]; then
        add 0.35 0.35 "# [pr_diff] (0.35): 6-level nested OrderedDict completes in <30s"
    else
        add 0.35 0.0 "# [pr_diff] (0.35): 6-level nested OrderedDict completes in <30s (too slow: ${ELAPSED_MS}ms)"
    fi
else
    EXIT_CODE=$?
    # ty returns non-zero for type errors, which is fine — we care about it finishing
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "TIMEOUT: Did not complete within 30s"
        add 0.35 0.0 "# [pr_diff] (0.35): 6-level nested OrderedDict completes in <30s (timeout)"
    else
        ELAPSED_MS=$(( ($(date +%s%N) - START) / 1000000 ))
        echo "Completed with exit code $EXIT_CODE in ${ELAPSED_MS}ms (type errors expected)"
        if [ "$ELAPSED_MS" -lt 30000 ]; then
            add 0.35 0.35 "# [pr_diff] (0.35): 6-level nested OrderedDict completes in <30s"
        else
            add 0.35 0.0 "# [pr_diff] (0.35): 6-level nested OrderedDict completes in <30s (too slow)"
        fi
    fi
fi

# [pr_diff] (0.35): Deeper nesting (8 levels) also completes in reasonable time
echo ""
echo "=== BEHAVIORAL: Deeper nested generic calls (8 levels) ==="
cat > /tmp/test_deep_generic.py <<'PYEOF'
from collections import OrderedDict
OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(("k", 1)))))))))
PYEOF

START=$(date +%s%N)
if timeout 60 cargo run --bin ty -- check /tmp/test_deep_generic.py 2>&1; then
    ELAPSED_MS=$(( ($(date +%s%N) - START) / 1000000 ))
    echo "Completed in ${ELAPSED_MS}ms"
    if [ "$ELAPSED_MS" -lt 60000 ]; then
        add 0.35 0.35 "# [pr_diff] (0.35): 8-level nested generic calls complete in <60s"
    else
        add 0.35 0.0 "# [pr_diff] (0.35): 8-level nested generic calls complete in <60s (too slow)"
    fi
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "TIMEOUT: Did not complete within 60s"
        add 0.35 0.0 "# [pr_diff] (0.35): 8-level nested generic calls complete in <60s (timeout)"
    else
        ELAPSED_MS=$(( ($(date +%s%N) - START) / 1000000 ))
        echo "Completed with exit code $EXIT_CODE in ${ELAPSED_MS}ms"
        if [ "$ELAPSED_MS" -lt 60000 ]; then
            add 0.35 0.35 "# [pr_diff] (0.35): 8-level nested generic calls complete in <60s"
        else
            add 0.35 0.0 "# [pr_diff] (0.35): 8-level nested generic calls complete in <60s (too slow)"
        fi
    fi
fi

# ── Pass-to-pass: Existing type inference still works correctly ──
# [repo_tests] (0.10): Run subset of ty_python_semantic tests to check for regressions
echo ""
echo "=== REGRESSION: Basic ty type checking still works ==="
cat > /tmp/test_basic.py <<'PYEOF'
from collections import OrderedDict

x: OrderedDict[str, int] = OrderedDict()
x["hello"] = 42
y = list(x.keys())
PYEOF

if timeout 30 cargo run --bin ty -- check /tmp/test_basic.py 2>&1; then
    add 0.10 0.10 "# [repo_tests] (0.10): Basic OrderedDict type checking works"
    echo "PASSED"
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        add 0.10 0.0 "# [repo_tests] (0.10): Basic OrderedDict type checking works (timeout)"
        echo "TIMEOUT"
    else
        # Non-zero exit from ty for type errors is acceptable
        add 0.10 0.10 "# [repo_tests] (0.10): Basic OrderedDict type checking works (exit $EXIT_CODE, type errors ok)"
        echo "PASSED (with type diagnostics)"
    fi
fi

# [repo_tests] (0.05): Non-generic code still type checks correctly
echo ""
echo "=== REGRESSION: Non-generic code ==="
cat > /tmp/test_nongeneric.py <<'PYEOF'
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)
reveal_type(result)
PYEOF

if timeout 15 cargo run --bin ty -- check /tmp/test_nongeneric.py 2>&1; then
    add 0.05 0.05 "# [repo_tests] (0.05): Non-generic type checking unaffected"
    echo "PASSED"
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        add 0.05 0.0 "# [repo_tests] (0.05): Non-generic type checking unaffected (timeout)"
    else
        add 0.05 0.05 "# [repo_tests] (0.05): Non-generic type checking unaffected (exit $EXIT_CODE ok)"
        echo "PASSED"
    fi
fi

# ── Config-derived: Rust code quality checks from AGENTS.md ──
# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76 @ 64c4c96
echo ""
echo "=== CONFIG: Import placement ==="
TARGET_FILE="crates/ty_python_semantic/src/types/infer/builder.rs"
# Check that no `use` statements appear inside function bodies
# (Look for `use` at indentation > 4 spaces within fn blocks — naive but effective)
if python3 -c "
import re
with open('$TARGET_FILE') as f:
    lines = f.readlines()
in_fn = False
bad = []
for i, line in enumerate(lines, 1):
    stripped = line.rstrip()
    # Detect function-local use statements (indented use inside impl blocks)
    if re.match(r'^        use ', line) or re.match(r'^            use ', line):
        # Skip if it's in a match arm or similar construct
        if 'use ' in stripped and '::' in stripped and not stripped.strip().startswith('//'):
            bad.append((i, stripped.strip()))
if bad:
    for b in bad:
        print(f'  Line {b[0]}: {b[1]}')
    exit(1)
else:
    exit(0)
" 2>&1; then
    add 0.05 0.05 "# [agent_config] (0.05): No function-local imports — AGENTS.md:76"
    echo "PASSED"
else
    add 0.05 0.0 "# [agent_config] (0.05): No function-local imports — AGENTS.md:76"
    echo "FAILED: Found local imports in function bodies"
fi

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79 @ 64c4c96
echo ""
echo "=== CONFIG: No unwrap/panic in new code ==="
# Check that the builder.rs file doesn't introduce unwrap() calls on the expression_cache
if python3 -c "
with open('$TARGET_FILE') as f:
    content = f.read()
# Look for .unwrap() near expression_cache usage
import re
# Find lines mentioning expression_cache that also have .unwrap()
lines = content.split('\n')
bad = []
for i, line in enumerate(lines, 1):
    if 'expression_cache' in line and '.unwrap()' in line:
        bad.append((i, line.strip()))
if bad:
    for b in bad:
        print(f'  Line {b[0]}: {b[1]}')
    exit(1)
exit(0)
" 2>&1; then
    add 0.05 0.05 "# [agent_config] (0.05): No unwrap() on expression_cache — AGENTS.md:79"
    echo "PASSED"
else
    add 0.05 0.0 "# [agent_config] (0.05): No unwrap() on expression_cache — AGENTS.md:79"
    echo "FAILED"
fi

# [pr_diff] (0.05): Anti-stub — the fix must actually modify builder.rs
echo ""
echo "=== STRUCTURAL: Anti-stub check ==="
if git diff --name-only HEAD 2>/dev/null | grep -q "builder.rs" || \
   git diff --cached --name-only 2>/dev/null | grep -q "builder.rs" || \
   ! git diff HEAD -- "$TARGET_FILE" 2>/dev/null | head -1 | grep -q "^$"; then
    # Check the file was actually modified from the base commit
    ORIG_HASH=$(git show HEAD:"$TARGET_FILE" 2>/dev/null | md5sum | cut -d' ' -f1)
    CURR_HASH=$(md5sum "$TARGET_FILE" | cut -d' ' -f1)
    if [ "$ORIG_HASH" != "$CURR_HASH" ]; then
        add 0.05 0.05 "# [pr_diff] (0.05): builder.rs was modified (anti-stub)"
        echo "PASSED"
    else
        add 0.05 0.0 "# [pr_diff] (0.05): builder.rs was modified (anti-stub)"
        echo "FAILED: builder.rs unchanged"
    fi
else
    add 0.05 0.0 "# [pr_diff] (0.05): builder.rs was modified (anti-stub)"
    echo "FAILED: builder.rs unchanged"
fi

# ── Summary ──
echo ""
echo "=== RESULTS ==="
printf "$DETAILS"
echo "Total: ${SCORE} / ${TOTAL}"

echo "${SCORE}" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
# behavioral: 0.35 + 0.35 = 0.70 max
# regression: 0.10 + 0.05 = 0.15 max
# config: 0.05 + 0.05 = 0.10 max
# structural: 0.05 max (anti-stub)
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(min(max(score - 0.70, 0), 0.15), 4),
    'config': round(min(max(score - 0.85, 0), 0.10), 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
print(open('/logs/verifier/reward.json').read())
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
