#!/bin/bash
# Gold solution: Apply the fix from PR apache/airflow#64734
# This PR introduces workers.celery.hpa section and deprecates workers.hpa

set -e

cd /workspace/airflow

# Idempotency check - skip if already applied
if grep -q "workers\.celery:" chart/values.yaml 2>/dev/null && grep -q "hpa:" <(sed -n '/workers\.celery:/,/^[^ ]/p' chart/values.yaml) 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Fetch the PR branch and apply the diff
git fetch origin pull/64734/head:pr-64734 --depth=100 2>/dev/null || \
    git fetch https://github.com/apache/airflow.git pull/64734/head:pr-64734 --depth=100

# Get the diff between base commit and PR and apply it
git diff HEAD...pr-64734 -- chart/ helm-tests/ | git apply --whitespace=fix -

echo "Gold patch applied successfully."
