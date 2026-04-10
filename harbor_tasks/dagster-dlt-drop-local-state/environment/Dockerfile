FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv ruff==0.15.0

# Create workspace and logs directories
RUN mkdir -p /workspace/dagster /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/dagster-io/dagster.git /workspace/dagster

# Checkout base commit
WORKDIR /workspace/dagster
RUN git checkout 095d02df486d2ab390f8d2385e1ef9413ecf37e0

# Install monorepo dependencies in the correct order using uv
# First install dagster-pipes (no internal deps)
WORKDIR /workspace/dagster/python_modules/dagster-pipes
RUN uv pip install -e "." --system

# Install dagster-shared (no internal deps)
WORKDIR /workspace/dagster/python_modules/libraries/dagster-shared
RUN uv pip install -e "." --system

# Install dagster core (depends on dagster-pipes and dagster-shared)
WORKDIR /workspace/dagster/python_modules/dagster
RUN uv pip install -e "." --system

# Install dagster-dlt using pip (avoid [test] dependencies that conflict)
WORKDIR /workspace/dagster/python_modules/libraries/dagster-dlt
RUN pip install -e "." --no-deps
RUN pip install dlt duckdb pytest

WORKDIR /workspace/dagster
