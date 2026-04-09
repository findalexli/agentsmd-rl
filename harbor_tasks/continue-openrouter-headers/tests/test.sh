#!/bin/bash
set -e

# Install pytest
pip install pytest --quiet

# Run tests and capture output
pytest /workspace/task/tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file (0 = fail, 1 = pass)
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Tests failed."
    exit 1
fi
