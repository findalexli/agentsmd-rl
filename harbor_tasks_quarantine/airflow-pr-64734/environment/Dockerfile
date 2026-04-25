# Dockerfile for airflow-helm-hpa-deprecation task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Helm (required for Helm template rendering)
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar xz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 93552c2bcb5815fb5e131e13a56995a7b8e97695

WORKDIR /workspace/airflow

# Install uv for dependency management
RUN pip install uv

# Install helm-tests dependencies
RUN cd helm-tests && uv sync --frozen || uv sync

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set up the environment
ENV PYTHONPATH=/workspace/airflow/helm-tests/tests
