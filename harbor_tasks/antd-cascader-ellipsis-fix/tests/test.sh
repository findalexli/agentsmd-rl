#!/bin/bash
set -e

# Create log directory if it doesn't exist
mkdir -p /logs/verifier

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet 2>/dev/null || true

# Run tests and capture results
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine if all tests passed
if python3 -m pytest test_outputs.py --tb=no -q 2>&1 | grep -q "passed"; then
    # Count how many tests passed
    passed_count=$(python3 -m pytest test_outputs.py --tb=no -q 2>&1 | grep -oP '\d+(?= passed)' || echo "0")
    total_count=$(python3 -m pytest test_outputs.py --collect-only -q 2>&1 | tail -1 | grep -oP '\d+(?= tests)' || echo "0")

    if [ "$passed_count" -eq "$total_count" ] && [ "$total_count" -gt 0 ]; then
        echo "1" > /logs/verifier/reward.txt
        echo "All tests passed!"
    else
        echo "0" > /logs/verifier/reward.txt
        echo "Some tests failed: $passed_count/$total_count passed"
    fi
else
    echo "0" > /logs/verifier/reward.txt
    echo "No tests passed"
fi

echo "Reward written to /logs/verifier/reward.txt"
cat /logs/verifier/reward.txt
