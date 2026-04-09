# syntax=docker/dockerfile:1
FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the Sui repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout fbb6960c6225c2a4406cd336a0899b54e53e4787

# Install Rust toolchain used by the repo
WORKDIR /workspace/sui
RUN rustup update

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
