# Licensed under the Apache License, Version 2.0
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Helm 3
RUN curl -fsSL https://get.helm.sh/helm-v3.15.0-linux-amd64.tar.gz | tar -xz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64 \
    && helm version

# Clone the repository with sparse checkout for chart and helm-tests
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git sparse-checkout init --cone \
    && git sparse-checkout set chart helm-tests dev/breeze/src/airflow_breeze/global_constants.py \
    && git checkout 79af23f696fc5e6fe3170211cd691ac4141863f8

# Install Python dependencies needed for helm tests
RUN pip install --no-cache-dir \
    pytest \
    jmespath \
    pyyaml \
    jsonschema \
    kubernetes

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
