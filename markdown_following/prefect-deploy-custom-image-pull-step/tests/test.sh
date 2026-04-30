#!/bin/bash
# Standardized test runner. Reward written to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/prefect

# Run the f2p + p2p suite. -p no:cacheprovider avoids polluting workspace.
python -m pytest /tests/test_outputs.py \
    -v \
    --tb=short \
    -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no rubric judge needed beyond reward; standalone_judge.py absent)

exit 0
