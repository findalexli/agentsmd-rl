# Dockerfile for airflow task-sdk CommsDecoder thread safety benchmark
FROM python:3.12-slim

# Install git and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit (sparse checkout for task-sdk only)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 6fd0142229eab87f23f95e5268aa80db1df8f9f3

WORKDIR /workspace/airflow

# Install task-sdk dependencies needed for testing
RUN pip install --no-cache-dir \
    pytest \
    msgspec \
    structlog \
    attrs \
    pydantic \
    pendulum

# Install task-sdk in editable mode (minimal install for the specific module)
RUN pip install --no-cache-dir -e ./task-sdk

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
