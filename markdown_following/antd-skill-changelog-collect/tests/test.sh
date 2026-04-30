#!/bin/bash
# Standardized verifier — DO NOT add task-specific logic here.
# Pytest exit code is the sole source of truth for reward.

set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/ant-design
python -m pytest /tests/test_outputs.py -v --tb=short \
    -p no:cacheprovider \
    --rootdir=/tests \
    -o "cache_dir=/tmp/.pytest_cache" \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
