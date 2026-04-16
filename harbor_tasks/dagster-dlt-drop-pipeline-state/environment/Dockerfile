FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone dagster repo at base commit (parent of merge commit)
# Using filter=blob:none for faster clone
ARG BASE_COMMIT=be55f8c00c583e070f8a0cb0518f7b49a85ab2d9
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git dagster && \
    cd dagster && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install uv for package management
RUN pip install uv

# Install dagster-dlt and its dependencies
# Need to install internal dependencies first (dagster-pipes, dagster-shared)
WORKDIR /workspace/dagster
RUN uv pip install --system \
    -e python_modules/dagster-pipes \
    -e python_modules/libraries/dagster-shared \
    -e python_modules/dagster

# Install dagster-dlt and test dependencies
# Note: Skip dagster-dg-cli test dependency as it conflicts with dev version
RUN uv pip install --system -e python_modules/libraries/dagster-dlt
# Install test dependencies separately (duckdb for testing)
RUN uv pip install --system duckdb

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

WORKDIR /workspace/dagster
