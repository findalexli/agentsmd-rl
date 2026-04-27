#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/superset

# Run pytest, write reward from exit code
python3 -m pytest /tests/test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $exit_code
