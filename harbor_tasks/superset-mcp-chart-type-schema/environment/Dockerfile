# Dockerfile for superset-mcp-chart-type-schema task
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit (before the fix)
WORKDIR /workspace
RUN git init /workspace/superset && \
    cd /workspace/superset && \
    git remote add origin https://github.com/apache/superset.git && \
    git fetch --depth=1 origin 8e811de5643022a97f6cb1890aa513197b7312e4 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/superset

# Install minimal Python dependencies needed for tests
# We need pydantic for the schema validation and superset_core for MCP decorators
RUN pip install --no-cache-dir \
    pydantic>=2.0 \
    pytest>=7.0 \
    pytest-timeout

# Install superset-core package (contains MCP decorators)
RUN pip install --no-cache-dir -e ./superset-core 2>/dev/null || \
    pip install --no-cache-dir superset-core 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/superset

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
