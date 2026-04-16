FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment for tests
RUN python3 -m pip install --break-system-packages pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Sui repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 3ac6f119a3ce41fccb9df0293a51e40ed6fadae3

WORKDIR /workspace/sui

# Pre-fetch dependencies to speed up builds
RUN cargo fetch

# Verify the code compiles at base commit
RUN cargo check -p sui-indexer-alt-framework-store-traits 2>&1 | head -50 || true
