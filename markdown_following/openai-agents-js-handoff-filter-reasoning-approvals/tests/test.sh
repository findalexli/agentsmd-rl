#!/usr/bin/env bash
# Standardized boilerplate. Do not add task-specific logic here.
set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    -o "cache_dir=/tmp/.pytest_cache" \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

echo "--- pytest log (tail) ---"
tail -n 200 /logs/verifier/pytest.log || true

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# Reserved for downstream evaluation tooling.
