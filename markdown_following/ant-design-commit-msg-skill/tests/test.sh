#!/usr/bin/env bash
# Standardized test runner: runs pytest and writes a binary reward to
# /logs/verifier/reward.txt based purely on pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    -o cache_dir=/tmp/.pytest_cache 2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"

# --- LLM Judge ---
# Track 2 (markdown_authoring config_edits semantic diff) is handled
# externally by the harness using eval_manifest.yaml.config_edits.
exit 0
