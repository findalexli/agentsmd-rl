#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short -p no:cacheprovider \
    --ctrf /logs/verifier/ctrf.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
