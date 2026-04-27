#!/usr/bin/env bash
# Standardized test harness. Do not add task-specific logic here.
set +e

mkdir -p /logs/verifier

cd /tests

# Run the canonical pytest suite. The reward is the literal pytest exit code.
python -m pytest test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    -p no:cacheprovider \
    > /logs/verifier/pytest.log 2>&1
RC=$?
cat /logs/verifier/pytest.log

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
