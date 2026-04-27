#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/hugo 2>/dev/null || true

python3 -m pytest /tests/test_outputs.py -v --tb=short --color=no 2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$status, reward=$(cat /logs/verifier/reward.txt)"
