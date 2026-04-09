FROM rust:1.85-slim

# Install Python, git, and build dependencies (including libclang for rocksdb)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at the base commit (shallow clone for speed)
# Using depth=500 to ensure we have enough history to reach the base commit
RUN git clone --depth 500 --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 53de0108098a9c041edc28ce4083f8dc9436a4d3

# Install cargo-nextest for running tests (pin version for Rust 1.85 compatibility)
RUN cargo install cargo-nextest@0.9.100 --locked

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
