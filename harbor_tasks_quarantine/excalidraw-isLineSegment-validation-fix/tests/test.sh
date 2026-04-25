#!/bin/bash
set -e

# Setup Python environment
if ! python3 -c "import pytest" 2>/dev/null; then
    # Try to install pytest system-wide first
    pip3 install pytest --quiet --break-system-packages 2>/dev/null || {
        # Fall back to virtual environment
        python3 -m venv /tmp/test-venv
        source /tmp/test-venv/bin/activate
        pip install pytest --quiet
    }
fi

# Run the tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
