# syntax=docker/dockerfile:1
FROM rust:1.85-slim

# Install Node.js (needed for VSCode extension) and Python (needed for pytest)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the sui repository at base commit
# Using --filter=blob:none for faster clone while keeping history needed for checkout
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 383a983d2b14715a4299227920188aa62089a723

# Install Rust components needed for the move-analyzer
RUN rustup component add rustfmt clippy

# Pre-build dependencies to cache them (optional but speeds up testing)
RUN cd /workspace/sui/external-crates/move/crates/move-analyzer && \
    cargo check 2>/dev/null || true

# Set up Python environment for tests
RUN python3 -m pip install pytest --break-system-packages 2>/dev/null || python3 -m pip install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
