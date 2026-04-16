FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Clone dagster repo at base commit (filter=blob:none for speed)
ARG BASE_COMMIT=3fc2834d865a46aa88a3271159edf52c5a0f07f2
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git /workspace/dagster && \
    cd /workspace/dagster && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/dagster

# Install dagster core package in editable mode
RUN uv pip install -e python_modules/dagster/ --system

# Install pytest and other test dependencies
RUN uv pip install pytest ruff==0.11.5 --system

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/dagster
