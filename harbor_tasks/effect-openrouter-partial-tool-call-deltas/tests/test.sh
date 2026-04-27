#!/usr/bin/env bash
# Standard test runner: pytest -> /logs/verifier/reward.txt {0|1}.
set -uo pipefail

mkdir -p /logs/verifier
REWARD_FILE=/logs/verifier/reward.txt
CTRF_FILE=/logs/verifier/ctrf.json

cd /tests

python3 -m pytest \
    -v --tb=short \
    --ctrf "$CTRF_FILE" \
    test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
  echo 1 > "$REWARD_FILE"
else
  echo 0 > "$REWARD_FILE"
fi

echo "reward=$(cat "$REWARD_FILE")"
exit 0
