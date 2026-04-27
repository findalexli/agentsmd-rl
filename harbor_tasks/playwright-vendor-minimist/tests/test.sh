#!/usr/bin/env bash
# Standardized test harness — runs pytest and writes binary reward.
set -uo pipefail

mkdir -p /logs/verifier

# pytest is preinstalled in the Dockerfile; bootstrap only if missing
# (e.g. on slim images where it's not part of the base layer).
if ! python3 -c "import pytest" 2>/dev/null; then
  pip3 install --no-cache-dir --break-system-packages \
      pytest==8.3.4 pytest-json-ctrf==0.4.1
fi

cd /tests
python3 -m pytest -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=$PYTEST_RC reward=$(cat /logs/verifier/reward.txt)"
