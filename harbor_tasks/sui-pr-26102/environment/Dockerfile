FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    libpq-dev \
    libclang-dev \
    clang \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for testing
RUN python3 -m pip install --break-system-packages pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repo at the base commit (shallow clone for speed)
WORKDIR /workspace
ARG BASE_COMMIT=2bf0af8d8048b75d7d7e6e46cde1958c40e43481
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui

# Pre-build dependencies for the relevant crates to speed up compilation
# This builds just the indexer-alt-jsonrpc crate and its dependencies
RUN cargo fetch 2>/dev/null || true
