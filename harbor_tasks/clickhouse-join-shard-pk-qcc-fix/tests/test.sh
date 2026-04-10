#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the test
cd /workspace/ClickHouse
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward based on pass_to_pass tests only
# fail_to_pass tests (test_patch_applied, test_contiguous_index_assignment, test_for_loop_indexing_logic, test_comment_explains_fix)
# are expected to fail at base commit before the fix is applied
F2P_TESTS="test_patch_applied|test_contiguous_index_assignment|test_for_loop_indexing_logic|test_comment_explains_fix"
P2P_FAILED=$(grep -E "FAILED" /logs/verifier/pytest.log | grep -vE "$F2P_TESTS" || true)
if [ -z "$P2P_FAILED" ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
