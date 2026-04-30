#!/usr/bin/env bash
# Runs test_outputs.py against the (possibly fixed) ty binary and writes a
# binary reward to /logs/verifier/reward.txt. Reward is the literal "1" if
# every pytest test passes, else "0".

set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest \
    -v \
    --tb=short \
    --maxfail=0 \
    -o cache_dir=/tmp/.pytest_cache \
    test_outputs.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $exit_code
