# Use Rust slim image as base
FROM rust:1.85-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    git \
    curl \
    python3 \
    python3-pip \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone the Sui repository at the base commit
# Using --depth to limit history for faster clone
ARG BASE_COMMIT=b62e4bf94eaaf96cb2d42b643ba92847bbf57be8
RUN git clone --filter=blob:none --depth=100 https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Set working directory to the repo
WORKDIR /workspace/sui

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Install pytest for testing
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Default command
CMD ["/bin/bash"]
