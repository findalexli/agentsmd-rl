#!/usr/bin/env bash
# Standardized test harness:
#   * runs pytest on /tests/test_outputs.py
#   * writes 0/1 reward derived from pytest's own exit code
#   * emits CTRF report at /logs/verifier/ctrf.json (via pytest-json-ctrf)
set -u
mkdir -p /logs/verifier

# pytest must be importable; if not, fail loud (do NOT mask with || true).
if ! python3 -c "import pytest" >/dev/null 2>&1; then
    echo "FATAL: pytest not installed in image" >&2
    echo 0 > /logs/verifier/reward.txt
    exit 1
fi

cd /tests
python3 -m pytest \
    --tb=short \
    -v \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
