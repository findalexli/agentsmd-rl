# Dockerfile for airflow-cleanup-prune-dirs task
FROM python:3.12-slim

# Install git and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 548e0a96a37940d1f14b37f7ae1b3a02cae1b83c

# Install minimal dependencies needed for airflow_breeze path_utils
RUN pip install --no-cache-dir rich

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
