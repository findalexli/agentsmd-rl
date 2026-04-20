#!/bin/bash
set -e

pip install --quiet pytest pytest-timeout
cd /workspace/mantine

# Run pytest and capture exit code, but don't let set -e kill us before writing reward
set +e
pytest /tests/test_outputs.py -v --tb=short --timeout=300 --no-header -q
PYRET=$?
set -e

# pytest: 0=pass, 1=fail. reward: 1=pass, 0=fail. So invert.
REWARD=$((1 - PYRET))
echo -ne "$REWARD" > /logs/verifier/reward.txt
exit 0