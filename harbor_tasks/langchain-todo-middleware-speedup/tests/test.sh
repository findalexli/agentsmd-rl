#!/bin/bash
set -e

# Install pytest if not available
pip install pytest -q

# Run the test_outputs.py tests and capture results
cd /tests

# Run tests with verbose output and short traceback
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Determine reward based on test results
# Count passed tests
total_tests=$(grep -c "^test_" /logs/verifier/test_output.log || true)
passed_tests=$(grep -c "PASSED" /logs/verifier/test_output.log || true)
failed_tests=$(grep -c "FAILED" /logs/verifier/test_output.log || true)

# Calculate reward (binary: all pass = 1, any fail = 0)
if [ "$failed_tests" -eq 0 ] && [ "$passed_tests" -gt 0 ]; then
    reward=1
else
    reward=0
fi

# Write reward to file
echo "$reward" > /logs/verifier/reward.txt

echo "Tests completed: $passed_tests passed, $failed_tests failed"
echo "Reward: $reward"

exit 0
