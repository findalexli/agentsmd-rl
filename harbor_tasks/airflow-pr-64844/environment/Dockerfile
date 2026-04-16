FROM python:3.12-slim

# Install git and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/airflow.git airflow && \
    cd airflow && \
    git checkout 4b0e876b470fcf47933f26898db2bf554c832ab1

# Install minimal dependencies for the constraints_version_check module
RUN pip install --no-cache-dir packaging rich pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/airflow
