#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
BEHAVIORAL=0.0
P2P=0.0
CONFIG=0.0
ANTISTUB=0.0
GATE_PASSED=1

cd /repo

########################################
# GATE: Code compiles
########################################
# [pr_diff] (gate): Modified Rust code compiles
echo "=== GATE: Building ruff ==="
if ! cargo build --bin ruff 2>&1; then
    echo "GATE FAILED: cargo build failed"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

RUFF="./target/debug/ruff"

########################################
# Create test notebook with consecutive empty cells
########################################
cat > /tmp/test_consecutive_empty.ipynb <<'NOTEBOOK'
{
 "cells": [
  {"cell_type": "code", "execution_count": null, "metadata": {}, "outputs": [], "source": ["1+1\n"]},
  {"cell_type": "code", "execution_count": null, "metadata": {}, "outputs": [], "source": ["\n", "\n"]},
  {"cell_type": "code", "execution_count": null, "metadata": {}, "outputs": [], "source": ["\n", "\n"]},
  {"cell_type": "code", "execution_count": null, "metadata": {}, "outputs": [], "source": ["\n", "\n"]}
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}
NOTEBOOK

########################################
# Behavioral 1: No panic on consecutive empty cells
########################################
# [pr_diff] (0.35): Consecutive empty notebook cells don't cause panic
echo "=== Behavioral 1: No panic on consecutive empty cells ==="
STDERR_FILE=$(mktemp)
set +e
OUTPUT=$($RUFF check --preview --select W391 /tmp/test_consecutive_empty.ipynb 2>"$STDERR_FILE")
EXIT_CODE=$?
STDERR_CONTENT=$(cat "$STDERR_FILE")
set -e
rm -f "$STDERR_FILE"

if echo "$STDERR_CONTENT" | grep -qi "panic"; then
    echo "FAIL: ruff panicked"
    echo "$STDERR_CONTENT" | head -20
else
    echo "PASS: No panic"
    TOTAL=$(python3 -c "print($TOTAL + 0.35)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.35)")
fi

########################################
# Behavioral 2: Correct W391 diagnostics produced
########################################
# [pr_diff] (0.30): W391 diagnostics emitted for cells with trailing newlines
echo "=== Behavioral 2: W391 diagnostics ==="
W391_COUNT=$(echo "$OUTPUT" | grep -c "W391" || true)
if [ "$W391_COUNT" -ge 3 ]; then
    echo "PASS: Found $W391_COUNT W391 diagnostics (expected >= 3)"
    TOTAL=$(python3 -c "print($TOTAL + 0.30)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.30)")
elif [ "$W391_COUNT" -ge 1 ]; then
    echo "PARTIAL: Found $W391_COUNT W391 diagnostics (expected >= 3)"
    TOTAL=$(python3 -c "print($TOTAL + 0.15)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + 0.15)")
else
    echo "FAIL: No W391 diagnostics found"
    echo "Output: $OUTPUT"
fi

########################################
# Pass-to-pass: W391 on regular .py file still works
########################################
# [pr_diff] (0.15): W391 detection on regular Python files unaffected
echo "=== Pass-to-pass: Regular .py file ==="
cat > /tmp/test_regular.py <<'PYFILE'
x = 1


PYFILE

set +e
PY_OUTPUT=$($RUFF check --preview --select W391 /tmp/test_regular.py 2>&1)
set -e

if echo "$PY_OUTPUT" | grep -q "W391"; then
    echo "PASS: W391 still works on .py files"
    TOTAL=$(python3 -c "print($TOTAL + 0.15)")
    P2P=$(python3 -c "print($P2P + 0.15)")
else
    echo "FAIL: W391 not triggered on .py file with trailing newlines"
    echo "Output: $PY_OUTPUT"
fi

########################################
# Config-derived: No bare .unwrap() in fix file
########################################
# [agent_config] (0.05): "Try hard to avoid patterns that require panic!, unreachable!, or .unwrap()" — AGENTS.md:79 @ 627e2a0
echo "=== Config: No bare .unwrap() ==="
FIX_FILE="crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs"
# Match .unwrap() but not .unwrap_or*, .unwrap_or_else, .unwrap_or_default
UNWRAP_COUNT=$(grep -cP '\.unwrap\(\)' "$FIX_FILE" || true)
if [ "$UNWRAP_COUNT" -eq 0 ]; then
    echo "PASS: No bare .unwrap() in fix file"
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: Found $UNWRAP_COUNT bare .unwrap() calls in $FIX_FILE"
fi

########################################
# Config-derived: No local use imports inside functions
########################################
# [agent_config] (0.05): "Rust imports should always go at the top of the file, never locally in functions" — AGENTS.md:76 @ 627e2a0
echo "=== Config: Imports at top of file ==="
LOCAL_IMPORTS=$(python3 -c "
import re
with open('$FIX_FILE') as f:
    content = f.read()
in_fn_body = False
brace_depth = 0
local_uses = 0
for line in content.splitlines():
    stripped = line.strip()
    for ch in stripped:
        if ch == '{':
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
    if re.match(r'(pub(\(crate\))?\s+)?fn\s+', stripped):
        in_fn_body = True
    if in_fn_body and brace_depth > 0 and re.match(r'use\s+', stripped):
        local_uses += 1
    if brace_depth <= 0:
        in_fn_body = False
print(local_uses)
" 2>/dev/null || echo "0")

if [ "$LOCAL_IMPORTS" -eq 0 ]; then
    echo "PASS: No local imports in functions"
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    CONFIG=$(python3 -c "print($CONFIG + 0.05)")
else
    echo "FAIL: Found $LOCAL_IMPORTS local import(s) inside function bodies"
fi

########################################
# Anti-stub: Changed files have real content
########################################
# [pr_diff] (0.10): Fix is non-trivial, not a stub
echo "=== Anti-stub check ==="
CELL_FILE="crates/ruff_notebook/src/cell.rs"
if [ -f "$FIX_FILE" ] && [ -f "$CELL_FILE" ]; then
    FIX_LINES=$(wc -l < "$FIX_FILE")
    CELL_LINES=$(wc -l < "$CELL_FILE")
    # Buggy versions have ~97 lines in fix file and ~348 in cell.rs
    # A real fix should maintain similar or greater line counts
    if [ "$FIX_LINES" -gt 50 ] && [ "$CELL_LINES" -gt 100 ]; then
        echo "PASS: Files have substantial content ($FIX_LINES / $CELL_LINES lines)"
        TOTAL=$(python3 -c "print($TOTAL + 0.10)")
        ANTISTUB=$(python3 -c "print($ANTISTUB + 0.10)")
    else
        echo "FAIL: Files seem too small ($FIX_LINES / $CELL_LINES lines)"
    fi
else
    echo "FAIL: Expected files not found"
fi

########################################
# Final score
########################################
echo ""
echo "=== TOTAL SCORE: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
json.dump({
    'reward': $TOTAL,
    'behavioral': $BEHAVIORAL,
    'pass_to_pass': $P2P,
    'config': $CONFIG,
    'anti_stub': $ANTISTUB
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
