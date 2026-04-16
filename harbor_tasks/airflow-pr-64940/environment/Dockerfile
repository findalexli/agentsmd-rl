# Dockerfile for airflow-sqlite-migration-fk task
FROM python:3.12-slim

# Install git and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository with minimal depth
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 8cbe7b9c4a18cf93c751fbdd0618ac92e70c20f4

# Install minimal dependencies for testing migrations
RUN pip install --no-cache-dir \
    sqlalchemy>=2.0 \
    alembic>=1.13 \
    pytest>=8.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
