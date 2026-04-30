#!/usr/bin/env bash
# Standardized test runner.
# Runs pytest on /tests/test_outputs.py inside the container; the binary
# reward (0/1) is taken from pytest's exit code.

set -u
mkdir -p /logs/verifier

cd /workspace/ant-design

CTRF_OUT=/logs/verifier/ctrf.json
PYTEST_LOG=/logs/verifier/pytest.log

pytest -v --tb=short \
    --ctrf "${CTRF_OUT}" \
    /tests/test_outputs.py 2>&1 | tee "${PYTEST_LOG}"
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: ${PYTEST_EXIT}"
echo "reward written: $(cat /logs/verifier/reward.txt)"
