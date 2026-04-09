#!/bin/bash

# Install pytest if needed
pip3 install pytest --quiet 2>/dev/null || true

# Run tests and capture output, checking the result
# Use || true to prevent exit on test failure
PYTEST_OUTPUT=$(python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1) || true

# Save output to log
echo "$PYTEST_OUTPUT" > /logs/verifier/pytest_output.txt

# Show output to console
echo "$PYTEST_OUTPUT"

# Write binary reward: 1 if all tests pass, 0 otherwise
if echo "$PYTEST_OUTPUT" | grep -q "failed"; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi
