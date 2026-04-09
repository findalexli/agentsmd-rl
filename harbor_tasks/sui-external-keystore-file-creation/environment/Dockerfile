FROM rust:1.85-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit (shallow clone for efficiency)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 4a9af930d043cc9f9bf7a9438ee3f25e4d26e741

# Pre-fetch dependencies to speed up builds
RUN cd /workspace/sui && cargo fetch -p sui-keys -p sui 2>/dev/null || true

# Set the working directory to the repo
WORKDIR /workspace/sui
