#!/bin/bash
set -uo pipefail

cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short --timeout=300
py_rc=$?

# Write binary reward: 1 if all tests passed (pytest exit 0), 0 otherwise
if [ $py_rc -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $py_rc
