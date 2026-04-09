#!/bin/bash
set -e

# Install pytest if not available
pip install pytest --quiet 2>/dev/null || true

# Run tests and capture result
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 or 1 based on pass/fail)
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $EXIT_CODE
