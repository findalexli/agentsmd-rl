# Dockerfile for apache/airflow#64932 benchmark task
# Tests Helm chart workers.celery.extraContainers & workers.kubernetes.extraContainers

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python test dependencies
RUN pip install --no-cache-dir \
    pytest \
    pyyaml \
    jmespath

# Clone the repository at base commit (sparse checkout for chart only)
WORKDIR /workspace
RUN git clone --filter=blob:none --sparse https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git sparse-checkout set chart helm-tests/tests/chart_utils && \
    git checkout 1c3ec8ab662534fb11187772c9ba1af29759ccba

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
