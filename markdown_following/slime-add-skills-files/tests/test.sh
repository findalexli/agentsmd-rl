#!/usr/bin/env bash
# Track 1 verifier: structural sanity check that the agent authored
# the five SKILL.md files with the required content. Track 2 (Gemini
# semantic-diff judgment over config_edits) is the real eval signal
# for this markdown_authoring task.

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short test_outputs.py --ctrf /logs/verifier/ctrf.json
status=$?

# --- LLM Judge ---
# Track 2 (Gemini semantic-diff over config_edits) is run by the harness;
# this script only handles Track 1 binary reward.

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- Reward ---"
cat /logs/verifier/reward.txt

exit 0
