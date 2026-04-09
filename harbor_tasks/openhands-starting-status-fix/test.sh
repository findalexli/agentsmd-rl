#!/bin/bash
set -e

cd /workspace/OpenHands/frontend

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the verifier tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
