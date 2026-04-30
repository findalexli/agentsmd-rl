#!/usr/bin/env bash
# Standard pytest runner: runs test_outputs.py and writes binary reward to
# /logs/verifier/reward.txt based on pytest's exit code (no grep/awk gates).

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (config_edits semantic-diff judgment via Gemini) is wired in via
# eval_manifest.yaml; nothing to do here.

exit 0
