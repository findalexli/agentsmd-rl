#!/usr/bin/env bash
set +e

SCORE=0
TARGET="crates/ruff_benchmark/benches/parser.rs"

cd /workspace/ruff 2>/dev/null || cd /repo

echo "=== Parser Benchmark Deallocation Fix ==="

add() { SCORE=$(python3 -c "print($SCORE + $1)"); }

# Helper: extract non-comment Rust source lines (strips // comments and /* */ blocks)
strip_comments() {
    python3 -c "
import re, sys
src = open('$TARGET').read()
# Remove block comments
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
# Remove line comments
src = re.sub(r'//.*', '', src)
print(src)
"
}

CLEAN=$(strip_comments)

# ── GATE: File exists and project compiles ──────────────────────────────
# [pr_diff] (gate): Modified file must exist
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# [pr_diff] (gate): Benchmark crate must compile (behavioral: proves code is valid Rust)
echo "Checking compilation..."
if ! cargo check -p ruff_benchmark --benches 2>&1; then
    echo "GATE FAIL: cargo check failed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: compiles"

# ── Fail-to-pass: behavioral checks (comment-stripped) ─────────────────

# [pr_diff] (0.30): Buggy b.iter(| pattern must be GONE from non-comment code
# The base code uses b.iter(|| { ... }) which includes deallocation in measurement.
# Any correct fix MUST replace this call. This check FAILS on the buggy baseline.
if echo "$CLEAN" | grep -qE 'b\.iter\s*\('; then
    echo "FAIL (0.30): Buggy b.iter() pattern still present — deallocation still measured"
else
    echo "PASS (0.30): b.iter() replaced — deallocation excluded from measurement"
    add 0.30
fi

# [pr_diff] (0.25): Deallocation-excluding API used in non-comment code
# iter_with_large_drop, iter_batched, iter_batched_ref, ManuallyDrop, mem::forget
# are all valid ways to exclude drop time from criterion measurement.
if echo "$CLEAN" | grep -qE 'iter_with_large_drop|iter_batched|iter_batched_ref|ManuallyDrop|mem::forget'; then
    echo "PASS (0.25): Deallocation-excluding API found in actual code"
    add 0.25
else
    echo "FAIL (0.25): No deallocation-excluding API in actual code"
fi

# [pr_diff] (0.10): CountVisitor dead code removed
# CountVisitor was only used to prevent compiler optimization — it's dead code.
if ! echo "$CLEAN" | grep -q 'CountVisitor'; then
    echo "PASS (0.10): CountVisitor dead code removed"
    add 0.10
else
    echo "FAIL (0.10): CountVisitor still present (dead code)"
fi

# [pr_diff] (0.05): Unused StatementVisitor/walk_stmt imports removed
if ! echo "$CLEAN" | grep -qE 'StatementVisitor|walk_stmt'; then
    echo "PASS (0.05): Unused visitor imports removed"
    add 0.05
else
    echo "FAIL (0.05): Unused visitor imports still present"
fi

# ── Pass-to-pass: existing structure preserved ──────────────────────────

# [pr_diff] (0.10): benchmark_parser function still exists
if echo "$CLEAN" | grep -q 'fn benchmark_parser'; then
    echo "PASS (0.10): benchmark_parser function preserved"
    add 0.10
else
    echo "FAIL (0.10): benchmark_parser function missing"
fi

# [pr_diff] (0.05): parse_module is still called in the benchmark
if echo "$CLEAN" | grep -q 'parse_module'; then
    echo "PASS (0.05): parse_module still called"
    add 0.05
else
    echo "FAIL (0.05): parse_module no longer called"
fi

# [pr_diff] (0.05): criterion macros preserved
if echo "$CLEAN" | grep -q 'criterion_group!' && echo "$CLEAN" | grep -q 'criterion_main!'; then
    echo "PASS (0.05): criterion macros preserved"
    add 0.05
else
    echo "FAIL (0.05): criterion macros missing"
fi

# ── Anti-stub ──────────────────────────────────────────────────────────

# [static] (0.05): File has meaningful content (not stubbed/gutted)
LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -ge 25 ]; then
    echo "PASS (0.05): File has meaningful content ($LINE_COUNT lines)"
    add 0.05
else
    echo "FAIL (0.05): File appears stubbed ($LINE_COUNT lines)"
fi

# ── Summary ─────────────────────────────────────────────────────────────

echo ""
echo "Total: $SCORE / 1.0"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('$SCORE')
data = {
    'reward': score,
    'behavioral': min(score, 0.70),
    'regression': 0.0,
    'config': 0.0,
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
print(json.dumps(data))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
