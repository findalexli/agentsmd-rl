#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short

# Write binary reward to /logs/verifier/reward.txt
# pytest exit code: 0 = all passed, 1 = some failed
if [ $? -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "0.0" > /logs/verifier/reward.txt
fi
