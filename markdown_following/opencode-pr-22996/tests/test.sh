#!/usr/bin/env bash
# Standardized test runner. Do not modify task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

# pytest-json-ctrf is already installed in the image; do not install at test time.
cd /tests
python3 -m pytest /tests/test_outputs.py \
  -v --tb=short \
  --ctrf /logs/verifier/ctrf.json \
  -o cache_dir=/tmp/.pytest_cache
status=$?

if [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (config-edit semantic diff) is handled out-of-band by the harness
# reading eval_manifest.yaml.config_edits. No judge invocation here.

exit 0
