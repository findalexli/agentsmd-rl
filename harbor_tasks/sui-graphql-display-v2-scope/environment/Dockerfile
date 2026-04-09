FROM rust:1.85-slim

# Install system dependencies: git for cloning, python3 for test harness, build tools, clang
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pytest \
    make \
    build-essential \
    clang \
    libclang-dev \
    llvm-dev \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set libclang path for bindgen
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib

# Clone the Sui repository at the base commit (before the fix)
WORKDIR /workspace
ARG BASE_COMMIT=4edd79bb00bb472bf7cfb56a891b7d6ab3e9db25
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Set up cargo environment
ENV CARGO_HOME=/root/.cargo
ENV PATH="${CARGO_HOME}/bin:${PATH}"

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch 2>/dev/null || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Default workdir for the task
WORKDIR /workspace/sui
