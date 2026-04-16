# Dockerfile for superset-mcp-null-fields task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 4e0890ee1fb422913aa4a6553cb135e43ebcc7f3

WORKDIR /workspace/superset

# Install Python dependencies - minimal set for testing the MCP service
RUN pip install --no-cache-dir \
    pydantic>=2.0 \
    sqlalchemy>=2.0 \
    flask \
    flask-sqlalchemy \
    flask-appbuilder \
    pytest \
    pytest-asyncio

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set PYTHONPATH to include the superset package
ENV PYTHONPATH=/workspace/superset
