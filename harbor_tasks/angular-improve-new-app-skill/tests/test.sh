#!/usr/bin/env bash
# Standard pytest runner. Runs /tests/test_outputs.py and writes a binary
# reward (literal "0" or "1") to /logs/verifier/reward.txt based on the
# pytest exit code.
set -u

mkdir -p /logs/verifier

cd /tests

python -m pytest test_outputs.py \
    -v \
    --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (Track 2 semantic-diff judging is performed externally by the harness
# using eval_manifest.yaml.config_edits; nothing to do here.)

exit 0
