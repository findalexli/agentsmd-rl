FROM rust:1.85-slim

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the Sui repo at the base commit
ARG BASE_COMMIT=47cc0bb95fba0d3dcdd38632a7f8d6e748f4b5ea
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout ${BASE_COMMIT}

# Pre-download Rust dependencies for faster builds
WORKDIR /workspace/sui
RUN cargo fetch --manifest-path external-crates/move/crates/move-compiler/Cargo.toml

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
