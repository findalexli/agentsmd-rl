FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Helm (needed for helm template rendering in tests)
RUN curl -fsSL https://get.helm.sh/helm-v3.14.0-linux-amd64.tar.gz | tar -xz -C /tmp && \
    mv /tmp/linux-amd64/helm /usr/local/bin/helm && \
    rm -rf /tmp/linux-amd64

# Clone the Airflow repository at the base commit
WORKDIR /workspace
ARG BASE_COMMIT=fc861cbf12857fbfed34d6e934706639d9d761f1
RUN git init /workspace/airflow && \
    cd /workspace/airflow && \
    git remote add origin https://github.com/apache/airflow.git && \
    git fetch --depth=1 origin fc861cbf12857fbfed34d6e934706639d9d761f1 && \
    git checkout FETCH_HEAD

# Install test dependencies
WORKDIR /workspace/airflow
RUN pip install pytest jmespath pyyaml --quiet

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
