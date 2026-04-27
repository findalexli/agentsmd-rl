#!/usr/bin/env bash
# Run pytest on test_outputs.py and write a binary reward to /logs/verifier/reward.txt.
# DO NOT add task-specific logic here.

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    test_outputs.py \
    -v --tb=short \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "reward: $(cat /logs/verifier/reward.txt)"
exit 0
