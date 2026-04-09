#!/bin/bash
set -e

cd /workspace/airflow

# Fetch and apply the gold patch directly from GitHub
curl -sL "https://github.com/apache/airflow/pull/64730.diff" | git apply -

# Verify the patch was applied by checking for a distinctive line
grep -q "worker.kubernetes.serviceAccountName" chart/templates/_helpers.yaml && echo "Patch applied successfully"
