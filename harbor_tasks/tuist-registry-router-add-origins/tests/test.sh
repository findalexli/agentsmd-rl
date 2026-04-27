#!/usr/bin/env bash
# Standard pytest-based verifier. Reward is the literal "0" or "1" derived
# from pytest's exit code, written to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
