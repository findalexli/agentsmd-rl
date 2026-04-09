#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run the tests
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Determine reward
if grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "0" > /logs/verifier/reward.txt
    echo "Tests FAILED"
else
    # Check all tests passed
    passed=$(grep -c "PASSED" /logs/verifier/pytest_output.txt || true)
    if [ "$passed" -gt 0 ]; then
        echo "1" > /logs/verifier/reward.txt
        echo "Tests PASSED"
    else
        echo "0" > /logs/verifier/reward.txt
        echo "No tests found or all skipped"
    fi
fi

cat /logs/verifier/reward.txt
