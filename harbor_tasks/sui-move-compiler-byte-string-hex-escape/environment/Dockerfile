FROM rust:1.92-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    curl \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git

WORKDIR /workspace/sui
RUN git checkout 92bc40908e2cd3a35255295fcde7d897f6e45910

# Pre-download dependencies for faster builds
RUN cd external-crates/move && cargo fetch
