#!/bin/bash

# Install pytest if needed
pip install -q pytest 2>/dev/null || true

# Run tests and capture output (don't exit on failure)
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt || true

# Count passed and failed tests from the output
PASSED=$(python3 -m pytest /tests/test_outputs.py -q --tb=no 2>&1 | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
FAILED=$(python3 -m pytest /tests/test_outputs.py -q --tb=no 2>&1 | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")

# Write binary reward
if [ "$FAILED" = "0" ] && [ "$PASSED" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
