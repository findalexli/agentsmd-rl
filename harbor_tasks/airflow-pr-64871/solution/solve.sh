#!/bin/bash
# Gold solution for apache/airflow#64871
# Applies the fix: Add workers.celery.hpa configuration to Helm chart

set -e

cd /workspace/airflow

# Check if fix is already applied (idempotency)
if grep -q "workers.celery.hpa.enabled" chart/templates/NOTES.txt 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Reset to the merge commit to get the complete fix
git fetch origin 8dc4305675a6817f55d5ebcc88367859da21beca --depth=1
git checkout 8dc4305675a6817f55d5ebcc88367859da21beca -- \
    chart/newsfragments/ \
    chart/templates/NOTES.txt \
    chart/templates/workers/worker-deployment.yaml \
    chart/values.schema.json \
    chart/values.yaml \
    helm-tests/tests/helm_tests/

echo "Fix applied successfully"
