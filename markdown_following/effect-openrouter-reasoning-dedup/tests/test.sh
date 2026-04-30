#!/usr/bin/env bash
# Standardized boilerplate. Runs pytest and writes a binary reward.

set -uo pipefail

mkdir -p /logs/verifier

pytest --tb=short -v /tests/test_outputs.py
RC=$?

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $RC
