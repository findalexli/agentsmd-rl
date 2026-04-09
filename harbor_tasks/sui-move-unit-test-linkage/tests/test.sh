#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || true

# Create log directory
mkdir -p /logs/verifier

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests pass, 0 otherwise
if python3 -m pytest test_outputs.py --tb=short -q 2>&1 | grep -q "passed"; then
    # Count failures - if any test fails, reward is 0
    if python3 -m pytest test_outputs.py --tb=short -q 2>&1 | grep -E "(FAILED|ERROR)" > /dev/null; then
        echo "0" > /logs/verifier/reward.txt
    else
        echo "1" > /logs/verifier/reward.txt
    fi
else
    echo "0" > /logs/verifier/reward.txt
fi
