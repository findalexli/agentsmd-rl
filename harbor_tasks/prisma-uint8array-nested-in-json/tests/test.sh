#!/usr/bin/env bash
mkdir -p /logs/verifier

cd /tests
pytest test_outputs.py -v --tb=short -p no:cacheprovider \
    --json-report --json-report-file=/logs/verifier/pytest_report.json
PYTEST_RC=$?

if [ "${PYTEST_RC}" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric scoring is performed by an external judge that reads
# /logs/verifier/pytest_report.json plus eval_manifest.yaml.
