#!/usr/bin/env bash
# Standardized test runner. Writes a binary reward (0/1) to
# /logs/verifier/reward.txt based on the pytest exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    -v \
    --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py
PYTEST_RC=$?

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: ${PYTEST_RC}"
echo "reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# (Reserved for downstream rubric evaluation. Reward above is binary from
# pytest's exit code.)
exit 0
