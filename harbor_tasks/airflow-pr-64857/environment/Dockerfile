# Benchmark task for apache/airflow#64857
# Adds workers.celery.waitForMigrations config section to Helm chart

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar xz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf linux-amd64

# Install Python dependencies for Helm tests
RUN pip install --no-cache-dir \
    pytest \
    jmespath \
    jsonschema \
    pyyaml

# Clone repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout a78f51911f028d795344d9ce2fbda49bffede563

WORKDIR /workspace/airflow

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
