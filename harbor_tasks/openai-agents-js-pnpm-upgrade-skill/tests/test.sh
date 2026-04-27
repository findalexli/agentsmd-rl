#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

set +e
pytest /tests/test_outputs.py \
    --tb=short -v \
    -p no:cacheprovider \
    --rootdir=/tests \
    --json-report --json-report-file=/logs/verifier/pytest_json.json \
    | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}
set -e

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: $PYTEST_RC, reward: $(cat /logs/verifier/reward.txt)"
