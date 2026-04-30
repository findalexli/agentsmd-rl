#!/usr/bin/env bash
set -u

mkdir -p /logs/verifier
cd /workspace/opencode/packages/opencode

# Run the pytest harness; reward is taken directly from pytest's exit code.
python3 -m pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    /tests/test_outputs.py
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
