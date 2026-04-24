FROM python:3.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone repo at base commit (shallow clone)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git && \
    cd lancedb && \
    git checkout 84bf022fb1b92b9adb805c7b95aa728aacd530b3

# Install Python dependencies for testing
RUN pip install pytest pyarrow numpy

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/lancedb

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
