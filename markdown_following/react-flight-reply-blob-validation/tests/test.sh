#!/usr/bin/env bash
# Standardised test runner.  Reward is binary, derived purely from
# pytest's exit code, written to /logs/verifier/reward.txt.

set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
PYTEST_EXIT=$?

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric scoring; gated on availability of a YAML manifest and
# a judge runtime.  Failures here do NOT change the reward.
if [ -f /tests/standalone_judge.py ] && [ -f /tests/eval_manifest.yaml ]; then
    python3 /tests/standalone_judge.py \
        --manifest /tests/eval_manifest.yaml \
        --output /logs/verifier/judge.json \
        || true
fi

exit 0
