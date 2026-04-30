#!/usr/bin/env bash

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short \
    -p no:cacheprovider \
    --ctrf=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
