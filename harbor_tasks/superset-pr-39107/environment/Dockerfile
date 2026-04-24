# Dockerfile for superset-mcp-truncation task
FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout 92747246fc7e562eef527034e8fcceec50aad9ab

WORKDIR /workspace/superset

# Install base dependencies from superset's requirements
# This ensures all imports work correctly
RUN pip install --no-cache-dir \
    -r requirements/base.txt \
    pytest \
    pytest-asyncio \
    --ignore-installed

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set PYTHONPATH so superset modules can be imported
ENV PYTHONPATH=/workspace/superset

WORKDIR /workspace/superset

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
