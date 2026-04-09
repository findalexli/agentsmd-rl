#!/bin/bash
set -uo pipefail

cd /tests
python3 -m pytest test_outputs.py -v 2>&1
exit_code=$?

# Write reward based on pytest exit code
if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $exit_code
