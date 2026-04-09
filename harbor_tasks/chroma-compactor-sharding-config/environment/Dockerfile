FROM rust:1.85-slim

# Install Python for pytest test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the chroma repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git

WORKDIR /workspace/chroma
RUN git checkout 6ee8c7542eb90d1544f7f1c3e8a35a6dbd042e04

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/chroma/rust/worker
RUN cargo fetch
