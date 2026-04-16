# Dockerfile for airflow-optional-theme-tokens task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow \
    && cd airflow \
    && git checkout 0d465d48d2b644095362f22c3ecc143689cfb60e

WORKDIR /workspace/airflow

# Install only the dependencies needed for testing the API types
# We need pydantic for the models being tested
RUN pip install --no-cache-dir \
    pydantic>=2.0 \
    pytest \
    pytest-timeout

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for task
WORKDIR /workspace/airflow
