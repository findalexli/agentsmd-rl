FROM rust:1.91-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install clippy and rustfmt for the active toolchain
RUN rustup component add --toolchain 1.91.0-x86_64-unknown-linux-gnu clippy rustfmt

# Install pytest and ruff
RUN pip3 install pytest ruff --break-system-packages

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git

WORKDIR /workspace/lancedb
RUN git checkout 613b9c1099d8c5d71093096e1026c0862b1d2d69

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch || true
