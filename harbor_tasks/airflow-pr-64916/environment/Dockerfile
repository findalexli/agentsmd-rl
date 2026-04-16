# Dockerfile for airflow-breeze-ci-commit-retry task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout 2eeff98486f794b014bd5ba74aeea5ecafca55a7

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Install breeze package dependencies
WORKDIR /workspace/airflow
RUN uv pip install --system -e dev/breeze

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
