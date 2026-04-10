#!/usr/bin/env bash
set -e

# Install pytest if needed
python3 -m pip install pytest --break-system-packages 2>/dev/null || python3 -m pip install pytest || true

# Run the Python test file and capture output
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Get the exit code of pytest (using PIPESTATUS to get it from the pipe)
PYTEST_EXIT_CODE=${PIPESTATUS[0]}

# Write binary reward file based on pytest exit code
# pytest exits 0 when all tests pass, non-zero when any fail
if [ "$PYTEST_EXIT_CODE" -eq 0 ]; then
    echo "All tests passed"
    printf '\x01' > /logs/verifier/reward.bin
else
    echo "Some tests failed (exit code: $PYTEST_EXIT_CODE)"
    printf '\x00' > /logs/verifier/reward.bin
fi
