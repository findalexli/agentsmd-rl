FROM python:3.12-slim

# Install git and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone repo with blob filter for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow

# Checkout the base commit (parent of merge)
WORKDIR /workspace/airflow
RUN git checkout 6888223bfcfa753c5b7539693dfd0eafb364cbb9

# Create logs directory for test output
RUN mkdir -p /logs/verifier

# Install pytest for running tests
RUN pip install --no-cache-dir pytest

WORKDIR /workspace/airflow
