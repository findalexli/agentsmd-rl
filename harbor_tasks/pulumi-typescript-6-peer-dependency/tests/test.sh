#!/usr/bin/env bash
# Standardized verifier entry point. Do not add task-specific logic here.
set +e

mkdir -p /logs/verifier

cd /tests
python3 -m pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest.log

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
