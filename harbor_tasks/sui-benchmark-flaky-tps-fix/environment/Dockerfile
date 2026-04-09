FROM rust:1.85-slim

# Install dependencies: python3 for pytest, git for cloning, build tools, and libclang for rocksdb
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=f6a774c2b71765b0bad451efe9b5ca171438eb72
RUN git clone --depth 50 --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-download Rust dependencies to speed up builds
RUN cd /workspace/sui && cargo fetch -p sui-benchmark || true

WORKDIR /workspace/sui
