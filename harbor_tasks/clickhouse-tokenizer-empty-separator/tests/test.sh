#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --quiet 2>/dev/null || true

# Run tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward (1 if all passed, 0 otherwise)
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi
