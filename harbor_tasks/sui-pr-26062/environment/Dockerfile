FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=2a6083bafec7a791806866cea60f03fd2e1beb65
RUN git clone --filter=blob:none --depth=100 https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui

# Build only the sui-display crate and its dependencies
# This pre-compiles dependencies for faster testing
RUN cargo check -p sui-display 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier
