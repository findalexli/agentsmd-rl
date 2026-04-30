#!/usr/bin/env bash
# Standard task test runner. Writes binary reward to /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --no-header \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
