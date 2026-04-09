#!/bin/bash
set -e

cd /workspace

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test file
cd /workspace/task
pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Extract the binary reward (last line should be JSON)
python3 -c "
import sys
import json

with open('/logs/verifier/test_output.log', 'r') as f:
    lines = f.readlines()

# Count passed tests
total = 0
passed = 0
for line in lines:
    if 'PASSED' in line:
        passed += 1
        total += 1
    elif 'FAILED' in line:
        total += 1

reward = passed / total if total > 0 else 0
result = {'total': total, 'passed': passed, 'reward': reward}
print(json.dumps(result))
" > /logs/verifier/reward.json

echo "--- REWARD ---"
cat /logs/verifier/reward.json
