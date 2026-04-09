#!/bin/bash
set -e

# Standardized test runner for benchmark tasks
# Installs pytest, runs test_outputs.py, writes binary reward

echo "Installing pytest..."
pip install -q pytest pyyaml

echo "Running tests..."
cd /workspace

# Run pytest and capture output
python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Calculate reward based on test results
# Count passed tests
PASSED=$(grep -c "PASSED" /logs/verifier/test_output.log || echo "0")
FAILED=$(grep -c "FAILED" /logs/verifier/test_output.log || echo "0")
TOTAL=$((PASSED + FAILED))

if [ "$TOTAL" -eq 0 ]; then
    REWARD=0.0
else
    REWARD=$(python3 -c "print(f'{${PASSED}/${TOTAL}:.2f}')")
fi

echo "Tests passed: $PASSED / $TOTAL"
echo "Reward: $REWARD"

# Write binary reward (0 or 1) based on all tests passing
if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

echo "Reward written to /logs/verifier/reward"
