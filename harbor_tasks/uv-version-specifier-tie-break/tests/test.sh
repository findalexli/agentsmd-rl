#!/usr/bin/env bash
# Standardized test harness. Do not add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

if ! python3 -c "import pytest" 2>/dev/null; then
    pip3 install --break-system-packages --no-cache-dir pytest==8.3.4
fi

cd /tests

python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf /logs/verifier/ctrf.json 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "PYTEST_RC=$PYTEST_RC"
echo "reward=$(cat /logs/verifier/reward.txt)"
