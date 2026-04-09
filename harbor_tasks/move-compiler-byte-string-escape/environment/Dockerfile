FROM rust:1.85-slim

# Install dependencies needed for testing and Python
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the Sui repository at base commit
# Using filter=blob:none for faster clone of large repo
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 92bc40908e2cd3a35255295fcde7d897f6e45910

# Pre-build dependencies to cache them
WORKDIR /workspace/sui/external-crates/move/crates/move-compiler
RUN cargo fetch

WORKDIR /workspace
