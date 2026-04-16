#!/bin/bash
set -e

# Install pytest if not present
pip install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log || true

# Count total tests collected by pytest (more reliable than grepping source)
total_tests=$(grep -oP 'collected \K[0-9]+' /logs/verifier/pytest.log || echo "0")
passed_tests=$(grep -c "PASSED" /logs/verifier/pytest.log || echo "0")

# Calculate reward (binary: 1 if all tests pass, 0 otherwise)
if [ "$passed_tests" -eq "$total_tests" ] && [ "$total_tests" -gt 0 ]; then
    reward=1
else
    reward=0
fi

echo "Tests: $passed_tests / $total_tests passed"
echo "Reward: $reward"

# Write reward to file
echo "$reward" > /logs/verifier/reward.txt
