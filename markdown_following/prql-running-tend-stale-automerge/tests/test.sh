#!/usr/bin/env bash
# Standardized harness: runs pytest, writes binary reward from exit code.
set -uo pipefail

mkdir -p /logs/verifier

# Bootstrap pytest if the base image doesn't ship it (no-op when already present).
if ! python3 -c "import pytest" 2>/dev/null; then
    pip install --quiet pytest==8.3.4 pyyaml==6.0.2
fi

cd /workspace/prql

python3 -m pytest /tests/test_outputs.py -v --tb=short
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "reward: $(cat /logs/verifier/reward.txt)"
exit 0
