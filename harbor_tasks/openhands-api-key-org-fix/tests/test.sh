#!/bin/bash
set -e

# Change to tests directory
cd /workspace/task/tests

# Install pytest and pytest-asyncio for async test support
pip install pytest pytest-asyncio -q

# Run the tests and capture output
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Check if all tests passed
if grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "0" > /logs/verifier/reward.txt
    echo "Tests FAILED"
    exit 1
elif grep -q "passed" /logs/verifier/test_output.log; then
    # Count passed vs total
    passed=$(grep -oP '\d+ passed' /logs/verifier/test_output.log | grep -oP '\d+' | head -1)
    total=$(grep -oP '\d+ items' /logs/verifier/test_output.log | grep -oP '\d+' | head -1)

    if [ -z "$passed" ] || [ -z "$total" ]; then
        echo "0" > /logs/verifier/reward.txt
        echo "Could not determine test results"
        exit 1
    fi

    # Calculate reward as passed/total
    reward=$(python3 -c "print($passed / $total)")
    echo "$reward" > /logs/verifier/reward.txt
    echo "Tests PASSED: $passed/$total (reward: $reward)"
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    echo "No test results found"
    exit 1
fi
