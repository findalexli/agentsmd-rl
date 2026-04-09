#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the test file
cd /workspace/task
timeout 300 python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
