#!/bin/bash
set -e

# Install pytest if needed
pip install pytest pytest-asyncio pytest-mock -q

# Run tests
cd /workspace/task/tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /tmp/test_output.txt

# Write binary reward
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo '{"passed": true, "reward": 1.0}' > /workspace/test_output.json
else
    echo '{"passed": false, "reward": 0.0}' > /workspace/test_output.json
fi

cat /workspace/test_output.json
exit $EXIT_CODE
