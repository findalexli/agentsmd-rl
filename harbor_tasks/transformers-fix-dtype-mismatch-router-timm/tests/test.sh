#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# Run the test suite. Pytest's exit code is the source of truth for reward.
python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    >/logs/verifier/pytest.log 2>&1
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest.log
echo "---"
echo "reward: $(cat /logs/verifier/reward.txt)"
exit 0
