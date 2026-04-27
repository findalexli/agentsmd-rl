#!/bin/bash
# Standardized harness: runs pytest and writes binary reward.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest test_outputs.py -v --tb=short \
  --ctrf /logs/verifier/ctrf.json \
  -o cache_dir=/tmp/.pytest_cache
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
exit 0
