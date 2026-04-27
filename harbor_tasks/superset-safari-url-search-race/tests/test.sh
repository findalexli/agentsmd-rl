#!/usr/bin/env bash
# Standardised verifier entrypoint. Runs pytest on the injected
# test_outputs.py and writes a binary reward to /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

cd /tests || { echo "[test.sh] /tests missing"; echo 0 > /logs/verifier/reward.txt; exit 0; }

python3 -m pytest \
    test_outputs.py \
    -v \
    --tb=short \
    --no-header \
    --json-report --json-report-file=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "${status}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "[test.sh] pytest exit=${status} reward=$(cat /logs/verifier/reward.txt)"
