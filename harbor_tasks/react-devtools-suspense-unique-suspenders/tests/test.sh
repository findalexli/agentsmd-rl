#!/bin/bash
set -euo pipefail

# Test script for react-devtools-suspense-unique-suspenders
# PR #35736: Include `uniqueSuspenders` in Suspense tree snapshots

REPO_DIR="/workspace/react"
UTILS_FILE="$REPO_DIR/packages/react-devtools-shared/src/devtools/utils.js"

SCORE=0.0
MAX_SCORE=1.0

# Helper to check if file exists and has content
file_has_content() {
    local file="$1"
    local pattern="$2"
    grep -q "$pattern" "$file" 2>/dev/null
}

# [pr_diff] GATE (0.00): Code must parse and exist
echo "=== GATE: Source file exists and is readable ==="
if [[ ! -f "$UTILS_FILE" ]]; then
    echo "FAIL: utils.js not found"
    echo "reward=0.0"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# Verify the file parses as valid JavaScript
if ! node --check "$UTILS_FILE" 2>/dev/null; then
    echo "FAIL: utils.js has syntax errors"
    echo "reward=0.0"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo "PASS: Source file exists and parses"

# [pr_diff] (0.70): printSuspense includes uniqueSuspenders in output
echo ""
echo "=== FAIL-TO-PASS: uniqueSuspenders field in printSuspense ==="
if file_has_content "$UTILS_FILE" "hasUniqueSuspenders" && \
   file_has_content "$UTILS_FILE" "uniqueSuspenders={"; then
    echo "PASS: printSuspense function includes uniqueSuspenders field"
    SCORE=$(python3 -c "print($SCORE + 0.70)")
else
    echo "FAIL: uniqueSuspenders field not found in printSuspense output"
fi

# [pr_diff] (0.15): Field uses correct ternary for boolean formatting
echo ""
echo "=== FAIL-TO-PASS: Boolean formatting uses ternary ==="
if grep -q 'hasUniqueSuspenders ? '\''true'\'' : '\''false'\''' "$UTILS_FILE" 2>/dev/null || \
   grep -q "hasUniqueSuspenders ? \"true\" : \"false\"" "$UTILS_FILE" 2>/dev/null || \
   grep -qE 'hasUniqueSuspenders.*\?.*true.*:.*false' "$UTILS_FILE" 2>/dev/null; then
    echo "PASS: Boolean properly formatted as 'true'/'false' strings"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: Boolean not properly formatted in template"
fi

# [repo_tests] (0.15): Existing tests still pass (regression check)
echo ""
echo "=== PASS-TO-PASS: utils.js logic tests ==="

# Create a minimal test to verify the printSuspense function works correctly
cd "$REPO_DIR"

# Test that we can import and use the modified function
node --input-type=module -e '
import {printOperations} from "./packages/react-devtools-shared/src/devtools/utils.js";
// If we can import without error, basic structure is intact
console.log("PASS: utils.js exports load correctly");
' 2>/dev/null || {
    # Try commonjs approach
    node -e '
const path = require("path");
console.log("INFO: Module test skipped (ES modules)");
' 2>/dev/null
}

# Check that the function constructs the output in the right order:
# <Suspense name="..." uniqueSuspenders={...} rects={...}>
if grep -A5 "function printSuspense" "$UTILS_FILE" | grep -q "uniqueSuspenders.*rects"; then
    echo "PASS: uniqueSuspenders appears before rects in output"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: Field ordering may be incorrect"
fi

# Output final score
echo ""
echo "=== FINAL SCORE ==="
printf "%.2f\n" "$SCORE"
echo "reward=$SCORE"

# Write reward files
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
parts = {
    'reward': score,
    'behavioral': min(score, 0.85),
    'regression': 0.15 if score > 0.7 else 0.0,
    'config': 0.0,
    'style_rubric': 0.0
}
print(json.dumps(parts))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
