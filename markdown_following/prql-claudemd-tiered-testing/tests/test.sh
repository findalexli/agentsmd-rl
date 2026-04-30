#!/usr/bin/env bash
# Standardized harness — do not modify task-specific logic in here.
set -u

mkdir -p /logs/verifier

cd /workspace/prql

cp /tests/test_outputs.py /workspace/prql/test_outputs.py

pytest -v --tb=short /workspace/prql/test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

rm -f /workspace/prql/test_outputs.py

echo "Reward: $(cat /logs/verifier/reward.txt)"
