#!/usr/bin/env bash
# Standardized test runner. Writes binary reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# pytest + ctrf reporter are baked into the image; do not install at test
# time. If they are missing, surface failure loudly rather than masking.
python3 -m pytest \
    --ctrf /logs/verifier/ctrf.json \
    -v --tb=short \
    test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge --------------------------------------------------------------
# (placeholder — Harbor's runtime injects the rubric judge here when
# scaffold_status.json reports success. Do not exit before this line.)
echo "Reward: $(cat /logs/verifier/reward.txt)"
exit 0
