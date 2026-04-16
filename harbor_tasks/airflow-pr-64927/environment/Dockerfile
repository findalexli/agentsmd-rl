# Dockerfile for airflow-skip-node-modules-cleanup task
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone airflow repository at base commit (sparse checkout for speed)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 44708bdb2a3bd58b66e9dc43bac84c08d1de876a

# Install minimal dependencies for the breeze utils module
# We only need the console and other utils that path_utils imports
WORKDIR /workspace/airflow
RUN pip install --no-cache-dir rich ruff

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
