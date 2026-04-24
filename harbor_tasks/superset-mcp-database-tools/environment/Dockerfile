FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the superset repository at base commit
# Using --filter=blob:none for partial clone to save time/space
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset && \
    cd /workspace/superset && \
    git checkout fc8c06f7a3ba4c0a5feeafbb522b876b5f017d45

# Install Python dependencies
# We need to install the development dependencies to run tests
RUN cd /workspace/superset && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest pydantic

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
