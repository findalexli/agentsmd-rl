FROM node:18-slim

# Install Python and required tools for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create log directory
RUN mkdir -p /logs/verifier

# Clone Superset repository at base commit (shallow clone for efficiency)
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/superset.git superset

# Checkout the base commit
WORKDIR /workspace/superset
RUN git checkout b8b2bdedf9bca608cbf0c4f0992be30877de300d

# Install frontend dependencies for the plugins we need to test
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps --ignore-scripts 2>&1 | tail -20 || true

# Set up working directory
WORKDIR /workspace/superset/superset-frontend
