FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git lancedb \
    && cd lancedb \
    && git checkout 1ba19d728e6bceb7148f27ad573583de3a96786a

WORKDIR /workspace/lancedb

# Install Python dependencies (just pytest and what we need for testing)
RUN pip install --no-cache-dir pytest pillow

# Pre-install lancedb Python package in development mode (needed for imports)
# Note: This is a Rust extension, so we install just the Python parts we need
RUN pip install --no-cache-dir -e python/python 2>/dev/null || \
    pip install --no-cache-dir lancedb || true

# Create log directory
RUN mkdir -p /logs/verifier

# Set Anthropic API key for judge
ENV ANTHROPIC_API_KEY=fw_3W5DyzZy8xYUQfwKK7Hghu

# Default working directory for task
WORKDIR /workspace/lancedb

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
