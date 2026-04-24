FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone dagster repo at base commit (sparse checkout for dagster-hightouch only)
ARG BASE_COMMIT=2c7102732263924f1ac8a83adae3cc9d5912b7d2
RUN git clone --filter=blob:none --no-checkout https://github.com/dagster-io/dagster.git dagster

WORKDIR /workspace/dagster

# Checkout base commit and sparse checkout only dagster-hightouch
RUN git checkout ${BASE_COMMIT} && \
    git sparse-checkout init --cone && \
    git sparse-checkout set python_modules/libraries/dagster-hightouch && \
    git checkout

# Install dagster and dependencies
RUN pip install --no-cache-dir \
    dagster \
    dagster-shared \
    requests \
    python-dateutil \
    pytest

# Set PYTHONPATH to include dagster-hightouch
ENV PYTHONPATH="/workspace/dagster/python_modules/libraries/dagster-hightouch:${PYTHONPATH}"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
