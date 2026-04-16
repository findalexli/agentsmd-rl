# Dockerfile for superset-playwright-timeout task
FROM python:3.12-slim

# Install git and required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone repository with shallow history
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset

# Checkout base commit (parent of merge commit)
WORKDIR /workspace/superset
RUN git checkout 3a3a6536b7ed9044ffaead2fbe0d8a944431925d

# Install minimal Python dependencies for running the unit tests
# We only need pytest and the testing dependencies, not full superset
RUN pip install --no-cache-dir \
    pytest \
    pytest-mock

# Create logs directory for verifier output
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
