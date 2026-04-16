#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# Installs pytest if needed and runs test_outputs.py

export PYTHONPATH="/workspace/containerd:$PYTHONPATH"
export PATH="/opt/venv/bin:$PATH"

# Run the tests
cd /workspace/containerd
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (1 if all tests pass, 0 otherwise)
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
