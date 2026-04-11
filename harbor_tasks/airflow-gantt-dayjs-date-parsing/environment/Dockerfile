# Dockerfile for Airflow Helm Chart Tests
# Tests the Helm chart rendering and validation

FROM python:3.11-slim-bookworm

# Install system dependencies including helm
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python dependencies for helm tests
RUN pip install --no-cache-dir \
    pytest \
    jmespath \
    pyyaml \
    jsonschema

# Set working directory (repo will be mounted here)
WORKDIR /workspace/airflow

# Create directories for volume mounts
RUN mkdir -p /tests /logs/verifier

# Set environment variables
ENV REPO=/workspace/airflow
ENV HELM_TEST_KUBERNETES_VERSION=1.29

# Default command runs the test script if mounted
CMD ["bash", "-c", "if [ -f /tests/test.sh ]; then bash /tests/test.sh; else echo 'No test.sh found'; fi"]
