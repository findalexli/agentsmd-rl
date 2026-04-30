#!/bin/bash
set -euo pipefail

cd /tests

set +e
python3 -m pytest test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
