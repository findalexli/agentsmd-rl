#!/bin/bash
set -euo pipefail

cd /workspace/openai-agents-js

pip3 install pytest==8.3.4 --break-system-packages -q 2>&1 | tail -1

set +e
pytest /tests/test_outputs.py -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

echo "--- LLM Judge ---"
python3 /tests/standalone_judge.py 2>&1

if [ $PYTEST_EXIT -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
