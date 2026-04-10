FROM rust:1.85-slim

# Install Python and other dependencies needed for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Chroma repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git

# Checkout the base commit
WORKDIR /workspace/chroma
RUN git checkout f206bbf894bd8a9f3bcf4db7d7a01425c70640d7

# Pre-compile dependencies to speed up subsequent builds
WORKDIR /workspace/chroma/rust
RUN cargo fetch

WORKDIR /workspace
