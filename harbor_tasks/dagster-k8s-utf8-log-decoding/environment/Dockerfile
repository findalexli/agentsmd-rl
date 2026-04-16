FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone dagster repo at base commit
ARG BASE_COMMIT=bff96c1a777298c1bf027e7eb1cedb556ddbe2ee
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git && \
    cd dagster && \
    git checkout ${BASE_COMMIT}

# Install uv for faster package management
RUN pip install --no-cache-dir uv

# Install dagster-k8s and its dependencies
WORKDIR /workspace/dagster/python_modules/libraries/dagster-k8s
RUN uv pip install -e . --system

# Also install dagster core
WORKDIR /workspace/dagster/python_modules/dagster
RUN uv pip install -e . --system

# Install pytest for testing
RUN uv pip install pytest --system

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo root for tests
WORKDIR /workspace/dagster
