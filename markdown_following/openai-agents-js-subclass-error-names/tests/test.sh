#!/usr/bin/env bash
# Standardized test harness: runs the pytest suite and writes a binary reward.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --maxfail=0 \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
RC=${PIPESTATUS[0]}

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
