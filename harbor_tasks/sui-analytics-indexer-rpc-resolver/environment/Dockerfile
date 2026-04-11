FROM rust:1.85-slim

# Install python3 for pytest runner and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set LIBCLANG_PATH for bindgen/rocksdb
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the Sui repository at base commit
# Using depth=1 since we only need the specific commit state
RUN git clone --depth 1 --filter=blob:none \
    https://github.com/MystenLabs/sui.git /workspace/sui \
    && cd /workspace/sui \
    && git fetch --depth 1 origin 591ac7c96a2877709479724edeea7038d01f064b \
    && git checkout 591ac7c96a2877709479724edeea7038d01f064b

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch -p sui-analytics-indexer || true

WORKDIR /workspace
