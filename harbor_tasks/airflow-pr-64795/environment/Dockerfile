FROM python:3.12-slim

# Install git and dependencies needed for cloning and testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the Airflow repository at base commit
# Using --filter=blob:none for faster clone (sparse checkout)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow

# Checkout the base commit
WORKDIR /workspace/airflow
RUN git checkout 8b03304883ca6237ce538f1af9408e5a6b74ca18

# Install uv for dependency management
RUN pip install uv

# Sync dependencies for the airflow-ctl-tests project (no dev deps for speed)
RUN uv sync --project airflow-ctl-tests --no-dev || true

# Set PYTHONPATH to include the test directory
ENV PYTHONPATH=/workspace/airflow/airflow-ctl-tests:/workspace/airflow/devel-common/src:/workspace/airflow/task-sdk/src

WORKDIR /workspace/airflow
