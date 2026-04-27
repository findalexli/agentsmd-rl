#!/usr/bin/env bash
# Standardized test runner. Reward is the literal '0' or '1' written to
# /logs/verifier/reward.txt, derived from pytest's exit code only.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/transformers || exit 1

# Run the behavioral suite. -v for human readability; --tb=short keeps the
# log compact; --json-ctrf provides a machine-readable report consumed by
# the harness to compute per-test verdicts.
python3 -m pytest /tests/test_outputs.py \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
