FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    clang \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Clone the Sui repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=404f123f44711212ac69f27762a49a57eb3454f0
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Setup for Move transactional tests
WORKDIR /workspace/sui

# Pre-build the Move transactional test runner to cache dependencies
RUN cargo build -p move-transactional-test-runner 2>&1 | head -50 || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
