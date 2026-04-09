#!/bin/bash
set -e

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward based on test results
if grep -q "PASSED" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

cat /logs/verifier/reward.txt
