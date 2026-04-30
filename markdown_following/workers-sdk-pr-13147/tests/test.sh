#!/bin/bash
set -uo pipefail

pytest /tests/test_outputs.py -v --tb=short
pytest_exit=$?

if [ $pytest_exit -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2: Gemini evaluates semantic equivalence of the agent-authored markdown
# vs the gold version. config_edits in eval_manifest.yaml defines the expected delta.
