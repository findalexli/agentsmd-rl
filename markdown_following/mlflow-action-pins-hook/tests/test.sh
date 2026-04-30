#!/bin/bash
# Standardized verifier — runs pytest, writes binary reward (0/1) from $? only.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

# Reward is the literal string "0" or "1" derived from pytest's exit code only.
# We use PIPESTATUS[0] because the pipe to `tee` would otherwise mask the real
# exit code.
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
