#!/bin/bash
set -e

cd /workspace/excalidraw

# Install pytest if not available
pip3 install pytest --quiet --break-system-packages 2>/dev/null || true

# Run the test file
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo '{"reward": 1, "status": "success"}' > /logs/verifier/reward.json
else
    echo '{"reward": 0, "status": "failure"}' > /logs/verifier/reward.json
fi

exit $EXIT_CODE
