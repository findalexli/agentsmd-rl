FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python dependencies for testing
RUN pip install --no-cache-dir \
    pytest \
    pyyaml \
    jmespath \
    jsonschema

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace
