#!/usr/bin/env bash
# Verifier for nextjs-turbopack-cell-read-toplevel
#
# Bug: try_read_task_cell in manager.rs incorrectly calls
# debug_assert_not_in_top_level_task unconditionally, preventing
# strongly-consistent cell reads from top-level tasks.
# The fix removes or conditionalizes that assertion.
#
# All checks are file-inspection based because:
# - turbopack workspace requires ~200+ crates and nightly Rust to compile
# - No Rust toolchain in Docker image (node:22-slim)
# - The relevant behavior is a debug_assert removal, verifiable by inspection
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

MANAGER="/workspace/next.js/turbopack/crates/turbo-tasks/src/manager.rs"
TEST_FILE="/workspace/next.js/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
if [ ! -f "$MANAGER" ] || [ ! -f "$TEST_FILE" ]; then
    echo "GATE FAILED: Required source files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED: Source files present"

###############################################################################
# Weight allocation:
#   GATE  [pr_diff]      (0.00): Core fix applied — gates everything
#   TEST 1 [pr_diff]     (0.40): debug_assert removed/conditionalized in try_read_task_cell
#   TEST 2 [pr_diff]     (0.30): Cell read test expects success, not panic
#   TEST 3 [pr_diff]     (0.15): Regression — debug_assert preserved in other methods
#   TEST 4 [pr_diff]     (0.10): Regression — eventual read test still expects panic
#   TEST 5 [structural]  (0.05): Anti-stub — manager.rs has substantial content
#   TOTAL                = 1.00
###############################################################################

SCORE="0.0"

###############################################################################
# GATE + TEST 1 [pr_diff] (0.40): The debug_assert_not_in_top_level_task call
# no longer fires unconditionally in try_read_task_cell. Accepts:
#   a) Complete removal of the assert (gold patch)
#   b) Conditional wrapping (e.g., only assert for non-strongly-consistent reads)
#   c) Any other approach that prevents unconditional assertion
###############################################################################
echo ""
echo "TEST 1 (GATE): [pr_diff] debug_assert no longer unconditional in try_read_task_cell"
# WHY inspection not call: Rust code requiring full turbopack workspace (~200
# crates, nightly toolchain) to compile. node:22-slim has no Rust.
GATE_PASS=0
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks/src/manager.rs") as f:
    src = f.read()

# Find the try_read_task_cell method body.
# Match from fn declaration to the next top-level fn or impl block.
pattern = r'(fn try_read_task_cell\b.*?)(?=\n    fn |\n    #\[track_caller\]\n    fn |\nimpl )'
match = re.search(pattern, src, re.DOTALL)
if not match:
    print("FAIL: Could not find try_read_task_cell method")
    sys.exit(1)

method_body = match.group(1)

# Check if the assert is completely removed (option a)
if 'debug_assert_not_in_top_level_task' not in method_body:
    print("PASS (removal): debug_assert_not_in_top_level_task fully removed from try_read_task_cell")
    sys.exit(0)

# Check if the assert is conditionalized (option b)
# The assert should be inside a conditional block, not at the top level of the method.
# Look for patterns like: if !strongly_consistent { assert } or if !options.strongly { assert }
lines = method_body.split('\n')
for i, line in enumerate(lines):
    if 'debug_assert_not_in_top_level_task' in line:
        # Check if there's a conditional guard in the preceding few lines
        context = '\n'.join(lines[max(0, i-5):i+1])
        # Accept any conditional wrapping (if, match, etc.)
        if re.search(r'\b(if|match)\b', context):
            print("PASS (conditionalized): debug_assert wrapped in conditional guard")
            sys.exit(0)

print("FAIL: debug_assert_not_in_top_level_task still fires unconditionally in try_read_task_cell")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    GATE_PASS=1
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.40:.4f}')")
    echo "  +0.40 (total: $SCORE)"
else
    echo "  GATE FAILED — core fix not applied, total score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# TEST 2 [pr_diff] (0.30): The cell read test expects success, not panic.
# Accepts any test structure where resolve_strongly_consistent + cell read
# does NOT have #[should_panic].
###############################################################################
echo ""
echo "TEST 2: [pr_diff] Cell read test expects success, not panic"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs") as f:
    src = f.read()

# Strategy: find any test function involving resolve_strongly_consistent + cell
# and verify it does NOT have #[should_panic].
# Also check the old name isn't still there with should_panic.

# Check 1: Old test name with should_panic should not exist
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'test_cell_read_in_top_level_task_fails' in line and 'fn ' in line:
        context = '\n'.join(lines[max(0, i-4):i+1])
        if 'should_panic' in context:
            print("FAIL: test_cell_read_in_top_level_task_fails still has #[should_panic]")
            sys.exit(1)

# Check 2: Find a cell-read test that expects success
# Split into test function blocks
test_pattern = r'((?:#\[(?:tokio::test|test)[^\]]*\]\s*(?:#\[should_panic[^\]]*\]\s*)?)?async\s+fn\s+(\w+)\s*\([^)]*\)[^{]*\{)'
found_cell_read_success = False

# Simpler approach: scan for resolve_strongly_consistent and check context
occurrences = [m.start() for m in re.finditer(r'resolve_strongly_consistent', src)]
for pos in occurrences:
    # Get the surrounding function context (look back for fn declaration)
    before = src[max(0, pos-1000):pos]
    fn_match = re.search(r'async\s+fn\s+(\w+)', before)
    if not fn_match:
        continue
    # Find the function's attribute block
    fn_start = before.rfind('async fn')
    if fn_start < 0:
        continue
    attr_region = before[max(0, fn_start-200):fn_start]
    if 'should_panic' not in attr_region:
        found_cell_read_success = True
        fn_name = fn_match.group(1)
        print(f"PASS: Test '{fn_name}' uses resolve_strongly_consistent without should_panic")
        break

if not found_cell_read_success:
    # Fallback: any function with cell read that doesn't have should_panic
    if 'resolve_strongly_consistent' in src and 'should_panic' not in src.split('resolve_strongly_consistent')[0].split('async fn')[-1]:
        found_cell_read_success = True
        print("PASS: Cell read test found without should_panic (fallback)")

if not found_cell_read_success:
    print("FAIL: No cell read test found that expects success")
    sys.exit(1)

sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.30:.4f}')")
    echo "  +0.30 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): Regression — debug_assert_not_in_top_level_task is
# preserved in try_read_task_output and try_read_local_output. These ARE
# eventually consistent and should keep the guard.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] debug_assert preserved in other methods"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks/src/manager.rs") as f:
    src = f.read()

# The assert should still exist in try_read_task_output and/or try_read_local_output.
# Check that at least 2 calls remain in the file overall (these are in other methods).
count = src.count('debug_assert_not_in_top_level_task')
if count < 2:
    print(f"FAIL: Expected >=2 remaining debug_assert_not_in_top_level_task calls, found {count}")
    print("  The assert should be preserved in try_read_task_output and try_read_local_output")
    sys.exit(1)

# Verify at least one is in try_read_task_output specifically
output_pattern = r'fn try_read_task_output\b.*?(?=\n    fn |\n    #\[track_caller\]\n    fn |\nimpl )'
output_match = re.search(output_pattern, src, re.DOTALL)
if output_match and 'debug_assert_not_in_top_level_task' in output_match.group(0):
    print(f"PASS: {count} calls remain; confirmed in try_read_task_output")
    sys.exit(0)

# Fallback: just trust the count
if count >= 2:
    print(f"PASS: {count} debug_assert_not_in_top_level_task calls remain in file")
    sys.exit(0)

print("FAIL: Could not confirm assert preservation")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.15:.4f}')")
    echo "  +0.15 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): Regression — eventual read test still expects panic.
# test_eventual_read_in_top_level_task_fails should retain #[should_panic].
###############################################################################
echo ""
echo "TEST 4: [pr_diff] Eventual read test still expects panic"
python3 << 'PYEOF'
import re, sys

with open("/workspace/next.js/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs") as f:
    src = f.read()

# Look for a test about eventual reads that still expects panic
# Accept any function name containing "eventual" with should_panic
lines = src.split('\n')
found = False

for i, line in enumerate(lines):
    if 'eventual' in line.lower() and 'fn ' in line:
        context = '\n'.join(lines[max(0, i-4):i+1])
        if 'should_panic' in context:
            fn_name = re.search(r'fn\s+(\w+)', line)
            name = fn_name.group(1) if fn_name else "unknown"
            print(f"PASS: Eventual read test '{name}' still expects panic")
            found = True
            break

if not found:
    # Broader fallback: file has should_panic somewhere and "eventual" somewhere
    if 'should_panic' in src and 'eventual' in src.lower():
        print("PASS: File contains eventual read test with should_panic (fallback)")
        found = True

if not found:
    print("FAIL: No eventual read panic test found")
    sys.exit(1)

sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.10:.4f}')")
    echo "  +0.10 (total: $SCORE)"
else
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# TEST 5 [structural] (0.05): Anti-stub — manager.rs has substantial content
###############################################################################
echo ""
echo "TEST 5: [structural] Anti-stub check on manager.rs"
LINE_COUNT=$(wc -l < "$MANAGER")
if [ "$LINE_COUNT" -gt 1000 ]; then
    SCORE=$(python3 -c "print(f'{float(\"$SCORE\") + 0.05:.4f}')")
    echo "  PASS: manager.rs has $LINE_COUNT lines (>1000)"
    echo "  +0.05 (total: $SCORE)"
else
    echo "  FAIL: manager.rs only has $LINE_COUNT lines — possible stub"
    echo "  +0.00 (total: $SCORE)"
fi

###############################################################################
# FINAL SCORE
###############################################################################
echo ""
echo "============================================"
echo "FINAL SCORE: $SCORE"
echo "============================================"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
