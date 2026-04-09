FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install uv

# Set up working directory
WORKDIR /workspace

# Clone the dagster repo at the base commit
# Using depth=500 to have enough history but keep it reasonably small
ARG BASE_COMMIT=f44352a8a384296e999c33df60bb785bd69953c4
RUN git clone --filter=blob:none --depth=500 https://github.com/dagster-io/dagster.git /workspace/dagster && \
    cd /workspace/dagster && \
    git checkout ${BASE_COMMIT}

# Install pytest for running tests
RUN uv pip install --system pytest

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/dagster
