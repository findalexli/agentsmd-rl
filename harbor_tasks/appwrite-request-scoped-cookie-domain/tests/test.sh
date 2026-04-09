#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v --tb=short

# Write binary reward for harness
if [ $? -eq 0 ]; then
    echo '{"passed": true}' > /logs/verifier/reward.json
else
    echo '{"passed": false}' > /logs/verifier/reward.json
fi
