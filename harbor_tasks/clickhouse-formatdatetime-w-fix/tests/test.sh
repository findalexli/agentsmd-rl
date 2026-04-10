#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run pytest on all tests
cd /workspace/ClickHouse
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Calculate reward based on test results
# Count passed tests
PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")
FAILED=$(grep -c "FAILED" /logs/verifier/test_output.log || echo "0")
TOTAL=$(grep -c "test_outputs.py::" /logs/verifier/test_output.log || echo "0")

# Write reward file
echo "Total tests: $TOTAL, Passed: $PASSED, Failed: $FAILED" > /logs/verifier/reward.txt

# Exit with success (reward file indicates actual results)
exit 0
