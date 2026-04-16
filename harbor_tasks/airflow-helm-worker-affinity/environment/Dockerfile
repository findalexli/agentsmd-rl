# Dockerfile for airflow-helm-worker-affinity benchmark task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar xz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64

# Install Python test dependencies
RUN pip install --no-cache-dir \
    pytest \
    pyyaml \
    jmespath \
    jsonschema

# Clone the airflow repo at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git \
    && cd airflow \
    && git checkout bc26d6b135d9a2b6b60e6b3208328adab88b03c4

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
