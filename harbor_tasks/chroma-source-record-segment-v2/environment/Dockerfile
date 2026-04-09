FROM rust:1.85-slim

# Install system dependencies and Python for testing
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
# Using --depth to limit history since this is a large repo
RUN git clone --depth 100 --filter=blob:none https://github.com/chroma-core/chroma.git chroma \
    && cd chroma \
    && git checkout 320068e0817387ad35a47e0cef8038d45b2992da

# Pre-build dependencies to cache them (optional but speeds up tests)
WORKDIR /workspace/chroma/rust

# Build the worker crate to cache dependencies
RUN cargo check --package chroma-worker 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace
WORKDIR /workspace
