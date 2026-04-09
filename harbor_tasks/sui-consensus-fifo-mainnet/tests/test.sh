#!/bin/bash
set -e

# Install pytest and run tests (use --break-system-packages for externally managed Python)
pip install pytest --quiet --break-system-packages || pip install pytest --quiet

# Run the test file
cd /tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
