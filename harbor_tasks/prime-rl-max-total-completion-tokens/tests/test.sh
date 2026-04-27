#!/bin/bash
# Standardized test runner. Writes binary reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace

python -m pytest /tests/test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
