#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run pytest on all tests
cd /workspace/ClickHouse
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Calculate reward based on test results
# Count structural tests (fail-to-pass) - these must pass for reward=1
STRUCTURAL_FAILED=$(grep -E "TestCodeStructure::test_.*FAILED" /logs/verifier/test_output.log | wc -l || echo "0")

# Write binary reward: 1 if no structural tests failed, 0 otherwise
if [ "$STRUCTURAL_FAILED" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
