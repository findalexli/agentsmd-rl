# Dockerfile for airflow-breeze-ci-upgrade-commit-retry task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit with blob filter
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 15faf7eadfaa8e5ca9788b926c44563178d31ffb

WORKDIR /workspace/airflow

# Install minimal dependencies needed for testing (breeze's click-based CLI)
RUN pip install --no-cache-dir click rich

# Create logs directory
RUN mkdir -p /logs/verifier

# Set the working directory
WORKDIR /workspace/airflow
