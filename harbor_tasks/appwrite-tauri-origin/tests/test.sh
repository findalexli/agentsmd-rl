#!/bin/bash
set -e

cd /workspace

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test file and capture output
pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward file based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
