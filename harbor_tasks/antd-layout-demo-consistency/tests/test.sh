#!/bin/bash
set -e

# Install pytest if not available
pip install pytest --quiet --break-system-packages || pip install pytest --quiet

# Run tests and capture output
cd /workspace
pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

exit $exit_code
