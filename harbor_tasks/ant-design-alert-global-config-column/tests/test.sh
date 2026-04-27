#!/bin/bash
# Standardised reward emitter. DO NOT add task-specific logic here.
# Reward is the literal '0' or '1' coming directly from pytest's exit code.

set -uo pipefail

mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt

cd /workspace/ant-design

python3 -m pytest /tests/test_outputs.py \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
