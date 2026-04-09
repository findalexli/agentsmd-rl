#!/bin/bash
set -e

# Install pytest
pip3 install pytest --quiet --break-system-packages

# Run the test file
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Write binary reward file (0 or 1 for each test)
# Reward file format: 1 if all tests passed, 0 otherwise
python3 -c "
import subprocess
import sys

# Run pytest again quietly to check status
result = subprocess.run(['python3', '-m', 'pytest', '/tests/test_outputs.py', '-q'], capture_output=True)
passed = result.returncode == 0

with open('/logs/verifier/reward.txt', 'w') as f:
    f.write('1' if passed else '0')

sys.exit(0)  # Always exit successfully so this script doesn't fail
"
