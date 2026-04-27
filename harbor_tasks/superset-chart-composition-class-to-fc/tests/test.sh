#!/usr/bin/env bash
# Standardized harness: runs pytest, writes binary reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py \
    -v \
    --tb=short \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json

if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
