#!/usr/bin/env bash
# Standard pytest runner. Reward = pytest exit code → /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py -v --tb=short -p no:cacheprovider \
    --ctrf=/logs/verifier/ctrf.json \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest.log

exit 0
