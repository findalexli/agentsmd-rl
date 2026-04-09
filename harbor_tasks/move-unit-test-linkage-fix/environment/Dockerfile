FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the Sui repository at base commit
# Using filter=blob:none for faster clone while still getting file contents
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 89286c8e52b8b358b3bd895e40ec4ee2f991c742

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies for faster builds
WORKDIR /workspace/sui
RUN cargo fetch --manifest-path external-crates/move/crates/move-unit-test/Cargo.toml 2>/dev/null || true

WORKDIR /workspace
