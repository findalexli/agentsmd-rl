# Dockerfile for airflow-dag-startdate-tz-overflow task
FROM python:3.12-slim

# Install git, patch, and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the Airflow repository at the base commit (shallow)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 5baee8a5a58e56afa7788c193753ad3cf804aa58

# Create logs directory for verifier output
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
