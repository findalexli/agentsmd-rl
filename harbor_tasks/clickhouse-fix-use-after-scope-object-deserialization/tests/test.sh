#!/bin/bash
set -e

# Standardized test runner for benchmark tasks
# This file is boilerplate - do not modify

# Install pytest if needed
python3 -m pip install pytest pytest-timeout -q 2>/dev/null || true

# Run tests and capture results
cd /workspace/ClickHouse
python3 -m pytest /tests/test_outputs.py -v --tb=short --timeout=300 2>&1 | tee /logs/verifier/test_output.log || true

# Write binary reward (1 if all tests passed, 0 otherwise)
if python3 -m pytest /tests/test_outputs.py --tb=no -q --timeout=300 2>&1 | grep -q "passed"; then
    # Count failures
    FAILURES=$(python3 -m pytest /tests/test_outputs.py --tb=no -q --timeout=300 2>&1 | grep -c "FAILED" || true)
    if [ "$FAILURES" -eq 0 ]; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Test run complete. Reward: $(cat /logs/verifier/reward.txt)"
