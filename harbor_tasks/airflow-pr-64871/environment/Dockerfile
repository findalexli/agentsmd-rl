# Dockerfile for apache/airflow#64871 benchmark task
# Task: Add workers.celery.hpa configuration to Helm chart

FROM python:3.12-slim

# Install required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Clone repository at base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout fc861cbf12857fbfed34d6e934706639d9d761f1

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest pyyaml

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
