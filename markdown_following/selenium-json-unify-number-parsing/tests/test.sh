#!/usr/bin/env bash
# Standardized test runner. Exits 0 only when all tests pass; reward is
# written from pytest's exit code to /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

# pytest is pre-installed in the Dockerfile; no network at test time.
cd /tests
pytest test_outputs.py -v --tb=short -p no:cacheprovider
EXIT=$?

if [ $EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No additional rubric runner here — eval_manifest.yaml drives Gemini judging
#  out-of-band; reward.txt provides the binary oracle signal.)

exit $EXIT
