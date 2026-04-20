#!/bin/bash
set -e
cd /workspace/mlflow_repo

# Apply the fix patch
git fetch --filter=blob:none https://github.com/mlflow/mlflow.git 53f3ede8a60c5d67febd729710610bcd522b8e70
git checkout 53f3ede8a60c5d67febd729710610bcd522b8e70
