#!/bin/bash
set -e

# Install pytest (using --break-system-packages for Docker environment)
pip3 install pytest --quiet --break-system-packages

# Run tests
cd /logs/verifier
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee pytest_output.txt

# Count total tests and passed tests
TOTAL_TESTS=$(grep -E "^collected [0-9]+ items" pytest_output.txt | sed 's/collected //' | sed 's/ items//')
if [ -z "$TOTAL_TESTS" ]; then
    TOTAL_TESTS=$(grep -cE "::test_" pytest_output.txt 2>/dev/null || echo "0")
fi

# Count passed tests
PASSED_COUNT=$(grep -cE "::test_[^[:space:]]+ PASSED" pytest_output.txt 2>/dev/null || echo "0")

# Get total expected from collected line, or count test definitions
if [ -z "$TOTAL_TESTS" ] || [ "$TOTAL_TESTS" -eq 0 ]; then
    # Fallback: count test functions in test file
    TOTAL_TESTS=$(grep -c "^def test_" /tests/test_outputs.py 2>/dev/null || echo "15")
fi

# All tests must pass for reward=1
if [ "$PASSED_COUNT" -eq "$TOTAL_TESTS" ] && [ "$TOTAL_TESTS" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
