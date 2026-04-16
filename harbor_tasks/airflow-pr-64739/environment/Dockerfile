# Dockerfile for airflow-helm-worker-extra-containers task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python test dependencies
RUN pip install --no-cache-dir pytest pyyaml

# Clone the repository with filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow

# Checkout the base commit
WORKDIR /workspace/airflow
RUN git checkout 27258d567887a93f43af25a9d79d773198751bd9

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
