FROM python:3.11-slim

# Install git for cloning and basic utilities
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment for testing
RUN pip install --upgrade pip pytest

# Clone ClickHouse repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse

WORKDIR /workspace/ClickHouse
# Checkout base commit (parent of merge commit)
RUN git checkout 0ac8d1fb82e45ca6c903f5549d564e867fb422dd

# Initialize submodules needed for build
RUN git submodule update --init --depth=1 contrib/sysroot contrib/curl contrib/ssl contrib/zlib contrib/lz4 contrib/zstd contrib/cityhash \
    2>/dev/null || true

# Pre-create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
