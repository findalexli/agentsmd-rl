# Superset MCP Service - Certification Fields Task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (before fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 83ad1eca26bec5de6e6d908ebf3ba6aa8eea0c21

WORKDIR /workspace/superset

# Install minimal Python dependencies for MCP service testing
RUN pip install --no-cache-dir \
    pydantic>=2.0.0 \
    pytest>=7.0.0 \
    pytest-asyncio>=0.21.0

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/superset
