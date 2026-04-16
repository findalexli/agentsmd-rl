FROM python:3.12-slim

# Install system dependencies (including patch)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the airflow repo at the base commit
ARG BASE_COMMIT=44708bdb2a3bd58b66e9dc43bac84c08d1de876a
RUN git clone --filter=blob:none https://github.com/apache/airflow.git && \
    cd airflow && \
    git checkout ${BASE_COMMIT}

# Install pytest and other test dependencies
RUN pip install --no-cache-dir pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
