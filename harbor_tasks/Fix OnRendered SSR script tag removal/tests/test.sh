#!/bin/bash

# Install pytest if not present (use --break-system-packages for Debian-managed Python)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test result
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
