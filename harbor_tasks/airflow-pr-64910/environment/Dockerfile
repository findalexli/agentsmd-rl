# Dockerfile for airflow-helm-affinity task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Clone repository with sparse checkout (only chart and helm-tests)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git sparse-checkout init --cone && \
    git sparse-checkout set chart helm-tests && \
    git checkout 8dc4305675a6817f55d5ebcc88367859da21beca

WORKDIR /workspace/airflow

# Install Python dependencies for helm tests
RUN pip install --no-cache-dir \
    pytest \
    pytest-xdist \
    pyyaml \
    jmespath

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/airflow
