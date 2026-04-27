#!/usr/bin/env bash
# Standardized pytest-driven verifier.
# Reward is the literal "0" or "1" derived from pytest's exit status.
set -u

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 \
    | tee /logs/verifier/pytest.log
PYTEST_STATUS=${PIPESTATUS[0]}

if [ "$PYTEST_STATUS" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# Track 2 (rubric / config-edit semantic comparison) is handled by the
# harness-level Gemini judge, which reads eval_manifest.yaml. No work to do
# in test.sh; this trailing section ensures pytest is not the script's last
# action and keeps the judge block reachable.
exit 0
