FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Create workspace and logs directories
RUN mkdir -p /workspace/dagster /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git /workspace/dagster

# Checkout base commit
WORKDIR /workspace/dagster
RUN git checkout 095d02df486d2ab390f8d2385e1ef9413ecf37e0

# Install dagster-dlt and its dependencies
WORKDIR /workspace/dagster/python_modules/libraries/dagster-dlt
RUN uv pip install -e ".[test]" --system

# Also install dagster core
WORKDIR /workspace/dagster/python_modules/dagster
RUN uv pip install -e ".[test]" --system

WORKDIR /workspace/dagster
