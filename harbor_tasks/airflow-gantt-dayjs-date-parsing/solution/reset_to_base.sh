#!/bin/bash
# Reset files to base commit (6f56aa1fe0) - before the extraInitContainers fix

set -e

echo "Resetting to base state..."

# Add safe directory for git
git config --global --add safe.directory /repo

# Copy files from base commit (6f56aa1fe0) from /repo
# Use git show to get the base commit files

cd /repo

# 1. Reset pod-template-file.kubernetes-helm-yaml
git show 6f56aa1fe0:chart/files/pod-template-file.kubernetes-helm-yaml > /workspace/airflow/chart/files/pod-template-file.kubernetes-helm-yaml

# 2. Reset values.schema.json
git show 6f56aa1fe0:chart/values.schema.json > /workspace/airflow/chart/values.schema.json

# 3. Reset values.yaml
git show 6f56aa1fe0:chart/values.yaml > /workspace/airflow/chart/values.yaml

# 4. Reset NOTES.txt
git show 6f56aa1fe0:chart/templates/NOTES.txt > /workspace/airflow/chart/templates/NOTES.txt

# 5. Remove newsfragment file (didn't exist in base)
rm -f /workspace/airflow/chart/newsfragments/64741.significant.rst

# 6. Reset docs
git show 6f56aa1fe0:chart/docs/using-additional-containers.rst > /workspace/airflow/chart/docs/using-additional-containers.rst 2>/dev/null || true

# NOTE: We do NOT reset the test files - they should remain at gold state
# so they test the new functionality. The tests should fail on base code.

echo "Reset to base state successfully!"
