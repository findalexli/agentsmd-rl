# Benchmark task environment for apache/airflow#64773
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 4e06847c2cdeb17be1c947b7a9dffbfb34418835

# Install dependencies for the shared/logging package and pytest
WORKDIR /workspace/airflow
RUN pip install --no-cache-dir \
    pytest \
    structlog>=25.4.0 \
    msgspec>=0.19.0 \
    pygtrie>=2.5.0

# Create logs directory for verifier output
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
