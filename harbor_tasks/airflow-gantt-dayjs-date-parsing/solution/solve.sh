#!/bin/bash
# Apply the gold fix for extraInitContainers support
# This adds workers.celery.extraInitContainers and workers.kubernetes.extraInitContainers

set -e

echo "Applying fix for extraInitContainers support..."

# Add safe directory for git
git config --global --add safe.directory /repo

cd /workspace/airflow

# Copy files from gold commit (mounted at /repo)
# These are the fixed versions

# 1. Update pod-template-file.kubernetes-helm-yaml
cp /repo/chart/files/pod-template-file.kubernetes-helm-yaml chart/files/pod-template-file.kubernetes-helm-yaml

# 2. Update values.schema.json
cp /repo/chart/values.schema.json chart/values.schema.json

# 3. Update values.yaml
cp /repo/chart/values.yaml chart/values.yaml

# 4. Update NOTES.txt
cp /repo/chart/templates/NOTES.txt chart/templates/NOTES.txt

# 5. Create newsfragment file
mkdir -p chart/newsfragments
cp /repo/chart/newsfragments/64741.significant.rst chart/newsfragments/64741.significant.rst 2>/dev/null || true

# 6. Update docs
cp /repo/chart/docs/using-additional-containers.rst chart/docs/using-additional-containers.rst 2>/dev/null || true

# NOTE: Test files should already be at gold state (not modified by reset)
# but we ensure they're at gold state just in case
cp /repo/helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py
cp /repo/helm-tests/tests/helm_tests/airflow_core/test_worker.py helm-tests/tests/helm_tests/airflow_core/test_worker.py
cp /repo/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py

echo "Fix applied successfully!"
