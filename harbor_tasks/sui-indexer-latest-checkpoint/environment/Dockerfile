# Rust-based benchmark task for Sui indexer framework
FROM rust:1.85-slim-bookworm

# Install required dependencies for building Sui
RUN apt-get update && apt-get install -y \
    git \
    curl \
    clang \
    libclang-dev \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install --break-system-packages pytest asyncio

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at the base commit
# Using a shallow clone to reduce image size - only fetch the specific commit
RUN git clone --depth=1 --branch main https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=1 origin b9b9628b2040de6b8f02af1e59d7a119dd4bbc10 && \
    git checkout b9b9628b2040de6b8f02af1e59d7a119dd4bbc10

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set the working directory to the repo root for running tests
WORKDIR /workspace/sui
