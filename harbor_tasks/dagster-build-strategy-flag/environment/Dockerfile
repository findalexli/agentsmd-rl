FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install uv

# Set up working directory
WORKDIR /workspace

# Clone dagster repo at the base commit (shallow clone for speed)
# Using --filter=blob:none for a partial clone that saves space
RUN git clone --filter=blob:none --no-checkout https://github.com/dagster-io/dagster.git dagster

WORKDIR /workspace/dagster

# Checkout the base commit (parent of merge commit)
RUN git checkout 2bf0f9b68618e6a0f9010512fded4d9dc869b1bd

# Install the dagster-dg-cli package and its dependencies
RUN uv pip install -e python_modules/libraries/dagster-dg-cli --system

# Install pytest and other test dependencies
RUN uv pip install pytest pytest-mock responses pyyaml syrupy "ruff==0.11.5" --system

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /workspace/dagster
