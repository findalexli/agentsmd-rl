#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch from the diff file
git apply /solution/patch.diff

# Verify the changes were applied
echo 'Verifying patch application...'
if ! grep -q 'workers.kubernetes.extraContainers' chart/files/pod-template-file.kubernetes-helm-yaml; then
    echo 'ERROR: Patch was not applied correctly'
    exit 1
fi

echo 'Patch applied successfully'
