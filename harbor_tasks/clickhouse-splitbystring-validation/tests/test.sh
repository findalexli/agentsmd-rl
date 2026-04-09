#!/bin/bash
set -e

cd /tests

# Install pytest if not already available
python3 -m pip install --break-system-packages pytest pyyaml 2>/dev/null || python3 -m pip install pytest pyyaml 2>/dev/null || true

# Run tests and capture output
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed!"
fi

exit $EXIT_CODE
