FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    jq \
    yq \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Helm unittest plugin
RUN helm plugin install https://github.com/helm-unittest/helm-unittest.git

# Set up workspace
WORKDIR /workspace/airflow

# Clone the repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=afcde65e4d129817affb694fd5f214ddd1544013
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/airflow.git /tmp/airflow-clone && \
    cd /tmp/airflow-clone && \
    git checkout ${BASE_COMMIT} && \
    cp -r chart /workspace/airflow/chart && \
    cp -r helm-tests /workspace/airflow/helm-tests && \
    rm -rf /tmp/airflow-clone

# Install Python test dependencies
RUN pip install --no-cache-dir \
    pytest \
    pyyaml \
    jmespath \
    jsonschema

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory to the chart for helm commands
WORKDIR /workspace/airflow
