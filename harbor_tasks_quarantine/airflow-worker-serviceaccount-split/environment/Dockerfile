# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Set working directory
WORKDIR /workspace/airflow

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=a02fbaa00cc51bce42c4375ca65febbe5589d6b2
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/airflow.git /tmp/airflow \
    && cd /tmp/airflow \
    && git checkout ${BASE_COMMIT} \
    && mv chart /workspace/airflow/chart \
    && mv helm-tests /workspace/airflow/helm-tests \
    && rm -rf /tmp/airflow

# Install Python dependencies for helm-tests
RUN pip install --no-cache-dir pytest pyyaml

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/airflow
