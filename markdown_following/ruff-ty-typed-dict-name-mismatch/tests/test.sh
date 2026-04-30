#!/usr/bin/env bash
# Standardized harness test runner. Reward is pytest's exit code, written as
# a literal "0" or "1" to /logs/verifier/reward.txt.
set -u

mkdir -p /logs/verifier

# Bootstrap pytest only if missing (slim base images may lack it).
if ! python3 -c "import pytest" >/dev/null 2>&1; then
    pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 pytest-json-ctrf==0.3.5
fi

cd /tests || cd "$(dirname "$0")"

# Run pytest. CTRF JSON gives per-test status for the post-validation gate.
python3 -m pytest test_outputs.py \
    -v \
    --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    2>&1 | tee /logs/verifier/pytest.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
