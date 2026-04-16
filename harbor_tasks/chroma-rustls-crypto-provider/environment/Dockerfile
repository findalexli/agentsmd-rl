FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    cmake \
    python3 \
    python3-pip \
    protobuf-compiler \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the chroma repository at base commit (before fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git
WORKDIR /workspace/chroma
RUN git checkout a0870063aaf988890fc8f642dbe2e11008dc5571

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-build dependencies for faster test runs
WORKDIR /workspace/chroma/rust/tracing
RUN cargo fetch

WORKDIR /workspace/chroma
