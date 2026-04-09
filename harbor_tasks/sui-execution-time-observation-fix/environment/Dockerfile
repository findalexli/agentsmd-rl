FROM rust:1.92-slim

RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    libclang-dev \
    clang \
    librocksdb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the Sui repo at the base commit (shallow clone with filter for speed)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout bafd093c8ab75e4dd16d1e574bb808d7fcd1a4e2

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set environment variables for building
# Find the correct libclang path (use llvm-19 which is installed with clang-19)
ENV LIBCLANG_PATH=/usr/lib/llvm-19/lib
ENV ROCKSDB_LIB_DIR=/usr/lib
ENV ROCKSDB_INCLUDE_DIR=/usr/include

# Ensure cargo is in PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Install rustfmt and clippy for the toolchain version used by the repo (1.92)
# The rust-toolchain.toml file in the repo will switch to this version automatically
RUN rustup toolchain install 1.92 && \
    rustup component add rustfmt clippy --toolchain 1.92

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
