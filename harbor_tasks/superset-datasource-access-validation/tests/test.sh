#!/usr/bin/env bash
# Standardised reward-writer for Harbor benchmark tasks.
#
# Reward semantics:
#   * pytest exits 0  -> reward 1
#   * pytest exits !=0 -> reward 0
# The reward MUST be a literal "0" or "1" written to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python -m pytest -v --tb=short --maxfail=20 -o cache_dir=/tmp/.pytest_cache test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt) (pytest exit=${status})"
