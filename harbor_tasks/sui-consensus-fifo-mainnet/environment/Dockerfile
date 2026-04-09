FROM rust:1.85-slim

# Install dependencies: python3, git, build tools, and libclang for rocksdb
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set up cargo environment
ENV CARGO_HOME=/root/.cargo
ENV PATH=$CARGO_HOME/bin:$PATH

# Clone the Sui repo at the base commit
ARG BASE_COMMIT=d40b0d0711182de2605732a49cba1f07e007c5ee
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui \
    && cd /workspace/sui \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui

# Pre-build dependencies to cache them (optional optimization)
# RUN cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier
