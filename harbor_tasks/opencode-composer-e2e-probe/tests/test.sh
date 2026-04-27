#!/usr/bin/env bash
# Standardized harness: run pytest, write binary reward to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py \
    -v --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    > /logs/verifier/pytest.log 2>&1
RC=$?

cat /logs/verifier/pytest.log

if [ $RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Reserved hook for offline rubric judge; the harness invokes standalone_judge.py
# out-of-band when present. Nothing to do at test time.
exit 0
