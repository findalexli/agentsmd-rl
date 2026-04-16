#!/bin/bash
# Solution script for apache/airflow#64730
# Adds workers.celery.serviceAccount & workers.kubernetes.serviceAccount

set -e

cd /workspace/airflow

# Check if already applied (idempotency)
if [ -f "chart/templates/workers/worker-kubernetes-serviceaccount.yaml" ]; then
    echo "Patch already applied"
    exit 0
fi

# Fetch the merge commit
git fetch origin 59ddf5698ab7ada2edce24f284c827db5242b170 --depth=1

# Checkout the specific files from the merge commit
git checkout FETCH_HEAD -- \
    chart/files/pod-template-file.kubernetes-helm-yaml \
    chart/newsfragments/64730.significant.rst \
    chart/templates/NOTES.txt \
    chart/templates/_helpers.yaml \
    chart/templates/workers/worker-kubernetes-serviceaccount.yaml \
    chart/values.schema.json \
    chart/values.yaml

echo "Patch applied successfully"
