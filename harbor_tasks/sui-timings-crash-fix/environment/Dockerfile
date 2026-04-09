FROM rust:1.85-slim

# Install system dependencies including build tools for rocksdb
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    curl \
    python3 \
    python3-pip \
    # Build dependencies for rocksdb
    clang \
    llvm-dev \
    libclang-dev \
    # rocksdb dependencies
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment for rocksdb
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 6c3a7475b6fd4aea9b9f9443a6cfad01a135c036

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set default workdir
WORKDIR /workspace/sui
