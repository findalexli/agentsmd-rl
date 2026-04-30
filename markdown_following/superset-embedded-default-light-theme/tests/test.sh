#!/usr/bin/env bash
set -uo pipefail

# Copy the task-controlled test file into the repo so jest discovers it.
cp /tests/ThemeControllerInitialMode.test.ts \
   /workspace/superset/superset-frontend/src/theme/tests/ThemeControllerInitialMode.test.ts

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json
PYTEST_RC=$?

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest_exit=${PYTEST_RC}"
echo "reward=$(cat /logs/verifier/reward.txt)"
exit 0
