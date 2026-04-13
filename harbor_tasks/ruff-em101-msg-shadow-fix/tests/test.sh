#!/bin/bash
# Test runner script for Docker execution
# Note: pass_to_pass tests should all pass. fail_to_pass test is expected to fail
# before the fix is applied.

cd /tests

# Run pytest and capture output to a file
python -m pytest test_outputs.py -v --tb=short > /tmp/pytest_output.txt 2>&1
cat /tmp/pytest_output.txt

# Count total tests from collect-only (more reliable)
TOTAL_COUNT=$(python -m pytest test_outputs.py --collect-only -q 2>/dev/null | tail -1 | grep -oE '[0-9]+' | head -1)
[ -z "$TOTAL_COUNT" ] && TOTAL_COUNT=0

# Count pass_to_pass tests (test_repo_*)
P2P_COUNT=$(python -m pytest test_outputs.py --collect-only -q 2>/dev/null | grep -c "test_repo_")
[ -z "$P2P_COUNT" ] && P2P_COUNT=0

# Count fail_to_pass tests (test_fail_to_pass_*)
F2P_COUNT=$(python -m pytest test_outputs.py --collect-only -q 2>/dev/null | grep -c "test_fail_to_pass_")
[ -z "$F2P_COUNT" ] && F2P_COUNT=0

# Count how many passed from the verbose output
P2P_PASSED=$(grep -c "test_repo_.*PASSED" /tmp/pytest_output.txt 2>/dev/null)
[ -z "$P2P_PASSED" ] && P2P_PASSED=0

F2P_PASSED=$(grep -c "test_fail_to_pass_.*PASSED" /tmp/pytest_output.txt 2>/dev/null)
[ -z "$F2P_PASSED" ] && F2P_PASSED=0

echo ""
echo "Pass-to-pass tests: $P2P_PASSED / $P2P_COUNT passed"
echo "Fail-to-pass tests: $F2P_PASSED / $F2P_COUNT passed"

# All tests must pass for reward=1
if [ "$P2P_PASSED" -eq "$P2P_COUNT" ] && [ "$P2P_COUNT" -gt "0" ] && \
   [ "$F2P_PASSED" -eq "$F2P_COUNT" ] && [ "$F2P_COUNT" -gt "0" ]; then
    echo "All tests passed!"
    mkdir -p /logs/verifier
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "Some tests failed!"
    mkdir -p /logs/verifier
    echo "0" > /logs/verifier/reward.txt
    exit 1
fi
