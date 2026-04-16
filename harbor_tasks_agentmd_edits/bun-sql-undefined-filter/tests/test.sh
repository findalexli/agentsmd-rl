#!/bin/bash
set -e

# pytest writes 1 (pass) or 0 (fail) to reward.txt
cd /workspace/bun
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/pytest_output.txt

# Exit code indicates pass/fail
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
