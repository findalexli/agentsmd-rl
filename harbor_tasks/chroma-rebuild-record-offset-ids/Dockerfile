FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git chroma

# Checkout base commit (before the fix)
WORKDIR /workspace/chroma
RUN git checkout b5362de1b7412b96545776a843f977f3c10ba4ff

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/chroma/rust
RUN cargo fetch

# Default working directory
WORKDIR /workspace/chroma
