#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
TARGET="crates/ty_python_semantic/src/types/infer/builder.rs"

cd /workspace/ruff 2>/dev/null || cd /repo

echo "=== ty Union Alias Attribute Error Fix ==="

# ── GATE: File exists and crate compiles ────────────────────────────────
# [pr_diff] (gate): Modified file must exist
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# [pr_diff] (gate): ty must compile
echo "Building ty..."
if ! cargo build --bin ty 2>&1; then
    echo "GATE FAIL: cargo build --bin ty failed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: ty compiles"

TY_BIN=$(cargo metadata --format-version=1 --no-deps 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['target_directory'])" 2>/dev/null)/debug/ty
if [ ! -x "$TY_BIN" ]; then
    TY_BIN="./target/debug/ty"
fi

# ── Fail-to-pass: behavioral checks via ty check ───────────────────────

# Create test file for aliased union attribute access
TESTDIR=$(mktemp -d)
cat > "$TESTDIR/test_alias_union.py" << 'PYEOF'
class A:
    pass

class B:
    def do_b_thing(self) -> None:
        pass

type U = A | B

class C:
    def __init__(self, values: list[U]) -> None:
        self.values = values

    def f(self) -> None:
        for item in self.values:
            item.do_b_thing()
PYEOF

echo "Running ty check on aliased union test..."
TY_OUTPUT=$("$TY_BIN" check --python-version 3.12 "$TESTDIR/test_alias_union.py" 2>&1 || true)
echo "$TY_OUTPUT"

# [pr_diff] (0.35): ty emits unresolved-attribute for aliased union member
if echo "$TY_OUTPUT" | grep -q 'unresolved-attribute'; then
    echo "PASS (0.35): unresolved-attribute diagnostic emitted for aliased union"
    SCORE=$(python3 -c "print($SCORE + 0.35)")
else
    echo "FAIL (0.35): no unresolved-attribute diagnostic for aliased union"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.35)")

# [pr_diff] (0.30): error correctly identifies 'A' as the type missing the attribute
if echo "$TY_OUTPUT" | grep -i 'unresolved-attribute' | grep -q '`A`'; then
    echo "PASS (0.30): error correctly identifies A as missing do_b_thing"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "FAIL (0.30): error does not identify A as the type missing the attribute"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.30)")

# ── Pass-to-pass: explicit (non-aliased) union still reports correctly ──

cat > "$TESTDIR/test_explicit_union.py" << 'PYEOF'
class X:
    pass

class Y:
    def only_on_y(self) -> None:
        pass

def check(val: X | Y) -> None:
    val.only_on_y()
PYEOF

echo ""
echo "Running ty check on explicit union test (pass-to-pass)..."
TY_OUTPUT2=$("$TY_BIN" check --python-version 3.12 "$TESTDIR/test_explicit_union.py" 2>&1 || true)
echo "$TY_OUTPUT2"

# [pr_diff] (0.10): explicit union attribute error still works
if echo "$TY_OUTPUT2" | grep -q 'unresolved-attribute'; then
    echo "PASS (0.10): explicit union unresolved-attribute still works"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): explicit union unresolved-attribute broken"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# [pr_diff] (0.05): ty does NOT emit unresolved-attribute when all union members have the attr
cat > "$TESTDIR/test_no_false_positive.py" << 'PYEOF'
class P:
    def shared(self) -> None:
        pass

class Q:
    def shared(self) -> None:
        pass

type PQ = P | Q

def check(val: PQ) -> None:
    val.shared()
PYEOF

echo ""
echo "Running ty check on no-false-positive test (pass-to-pass)..."
TY_OUTPUT3=$("$TY_BIN" check --python-version 3.12 "$TESTDIR/test_no_false_positive.py" 2>&1 || true)
echo "$TY_OUTPUT3"

if ! echo "$TY_OUTPUT3" | grep -q 'unresolved-attribute'; then
    echo "PASS (0.05): no false positive for aliased union where all members have attr"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): false positive unresolved-attribute on valid aliased union"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# ── Config-derived checks ──────────────────────────────────────────────

# [agent_config] (0.05): "Rust imports should always go at the top of the file" — AGENTS.md:76
# Check that no use/extern crate statements appear inside function bodies in the target file
if ! python3 -c "
import re
content = open('$TARGET').read()
in_fn = False
brace_depth = 0
has_local_import = False
for line in content.splitlines():
    stripped = line.strip()
    if re.match(r'fn\s+\w+', stripped):
        in_fn = True
        brace_depth = 0
    if in_fn:
        brace_depth += stripped.count('{') - stripped.count('}')
        if brace_depth > 0 and re.match(r'use\s+', stripped):
            has_local_import = True
        if brace_depth <= 0 and in_fn and '{' in line:
            in_fn = brace_depth > 0
exit(0 if not has_local_import else 1)
"; then
    echo "FAIL (0.05): Local imports found inside functions (AGENTS.md:76)"
else
    echo "PASS (0.05): No local imports in functions"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# [agent_config] (0.05): "Try hard to avoid panic!/unreachable!/.unwrap()" — AGENTS.md:79
# Check the diff for new unwrap()/panic!/unreachable! calls
DIFF=$(git diff HEAD 2>/dev/null || true)
if [ -z "$DIFF" ]; then
    DIFF=$(git diff HEAD~1 2>/dev/null || true)
fi
NEW_UNWRAPS=$(echo "$DIFF" | grep '^+' | grep -cE '\.unwrap\(\)|panic!\(|unreachable!\(' || true)
if [ "$NEW_UNWRAPS" -eq 0 ]; then
    echo "PASS (0.05): No new unwrap()/panic!/unreachable! in diff"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): Found $NEW_UNWRAPS new unwrap()/panic!/unreachable! calls"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

# ── Anti-stub check ────────────────────────────────────────────────────

# [static] (0.10): Target file has meaningful content (not stubbed/gutted)
LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -ge 5000 ]; then
    echo "PASS (0.10): File has meaningful content ($LINE_COUNT lines)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): File appears stubbed ($LINE_COUNT lines, expected >=5000)"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

# Clean up
rm -rf "$TESTDIR"

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "Total: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed reward breakdown
python3 -c "
import json
score = float('$SCORE')
data = {'reward': score}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
