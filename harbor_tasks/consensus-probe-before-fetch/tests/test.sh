#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet 2>/dev/null || true

# Run the tests from the mounted /tests directory
cd /tests

# Run pytest and capture exit code (disable exit-on-error temporarily)
set +e
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log
exit_code=${PIPESTATUS[0]}
set -e

# Write binary reward based on test results
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
