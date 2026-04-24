FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the dagster repository at the base commit
# Using --filter=blob:none for faster clone (sparse checkout)
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git /workspace/dagster && \
    cd /workspace/dagster && \
    git checkout a75f1d9f9829f5306639d3db73f826a53051e101

# Set the working directory to the repo
WORKDIR /workspace/dagster

# Install pytest
RUN pip install pytest

# Install dagster-docker test dependencies (if pyproject.toml exists)
RUN cd /workspace/dagster/python_modules/libraries/dagster-docker && \
    pip install -e . --no-deps 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variable for the repo path
ENV DAGSTER_GIT_REPO_DIR=/workspace/dagster

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
