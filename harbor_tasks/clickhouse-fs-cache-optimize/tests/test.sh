#!/bin/bash
set -e

# Default to /tests if no argument provided
TEST_DIR="${1:-/tests}"
cd "$TEST_DIR"

# Install pytest if not available
pip3 install pytest pyyaml -q 2>/dev/null || true

# Run the tests and capture output
pytest test_outputs.py -v --tb=short 2>&1 | tee /tmp/test_output.txt

# Write binary reward (0 or 1) based on test results
if grep -q "FAILED" /tmp/test_output.txt; then
    echo "0" > /logs/verifier/reward.txt
    exit 1
else
    echo "1" > /logs/verifier/reward.txt
    exit 0
fi
