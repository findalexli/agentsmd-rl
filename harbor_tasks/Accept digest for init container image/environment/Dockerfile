FROM python:3.12-slim

# Install Helm and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Helm 3
RUN VERIFY_CHECKSUM=false curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Create necessary directories
RUN mkdir -p /workspace/dagster /workspace/task /logs/verifier 

# Create symlink for tests directory (tests will be mounted at /tests)
RUN ln -sf /tests /workspace/task/tests

# Install Python dependencies for testing
RUN pip install --no-cache-dir pytest pyyaml

WORKDIR /workspace
