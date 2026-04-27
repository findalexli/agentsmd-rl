#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest.log

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Pytest exit code: $PYTEST_RC"
echo "Reward: $(cat /logs/verifier/reward.txt)"
