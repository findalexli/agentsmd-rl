#!/bin/bash
set -e

# Install pytest for the test runner (handle externally-managed-environment)
pip install pytest --quiet --break-system-packages 2>/dev/null || pip install pytest --quiet 2>/dev/null || true

# Run the tests
cd /workspace/task
python3 tests/test_outputs.py

# Write binary reward for the framework
if [ $? -eq 0 ]; then
    echo '{"passed": true, "reward": 1.0}' > /logs/verifier/reward.json
else
    echo '{"passed": false, "reward": 0.0}' > /logs/verifier/reward.json
fi
