FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install uv for Python package management
RUN pip install uv

# Clone Airflow repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=bc26d6b135d9a2b6b60e6b3208328adab88b03c4
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/airflow.git /workspace/airflow \
    && cd /workspace/airflow \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/airflow

# Install Python dependencies for helm-tests
RUN uv pip install --system pytest pytest-helm-templates jmespath pyyaml

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
