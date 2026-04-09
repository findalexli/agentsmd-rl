FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-xdist \
    jmespath \
    pyyaml \
    jsonschema

# Create directories
RUN mkdir -p /workspace/airflow /logs/verifier

# Clone Airflow repo at base commit (shallow clone for efficiency)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout afcde65e4d129817affb694fd5f214ddd1544013

WORKDIR /workspace/airflow

# Verify the chart directory exists
RUN test -d chart || (echo "Chart directory not found" && exit 1)

# Pre-install Helm dependencies for the chart
WORKDIR /workspace/airflow/chart
RUN helm dependency build 2>/dev/null || true

WORKDIR /workspace/airflow
