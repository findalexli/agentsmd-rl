#!/bin/bash
# Standard test.sh - do not modify
set -e

cd /workspace/payload

# Install pytest
pip install -q pytest

# Run the test harness
python3 -c "
import subprocess
import sys

result = subprocess.run(
    ['python3', '/tests/test_outputs.py'],
    capture_output=True,
    text=True,
    timeout=600,
    cwd='/workspace/payload'
)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

# Write reward
if result.returncode == 0:
    with open('/logs/verifier/reward.txt', 'w') as f:
        f.write('1')
else:
    with open('/logs/verifier/reward.txt', 'w') as f:
        f.write('0')

sys.exit(result.returncode)
"