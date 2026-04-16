# Licensed under the Apache License, Version 2.0
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar -xzf - \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest pyyaml jmespath

# Clone the Apache Airflow repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout a02fbaa00cc51bce42c4375ca65febbe5589d6b2

# Update helm dependencies
WORKDIR /workspace/airflow/chart
RUN helm dependency update

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
