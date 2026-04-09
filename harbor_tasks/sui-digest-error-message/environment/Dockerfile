FROM rust:1.85-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Create workspace
WORKDIR /workspace

# Clone the sui repository at base commit (shallow clone for speed)
RUN git clone --depth=100 --filter=blob:none https://github.com/MystenLabs/sui.git

WORKDIR /workspace/sui

# Checkout the base commit (parent of merge commit)
RUN git checkout 08500756541c6fd66c81a59d1af1d819e997a189

# Pre-download dependencies to speed up subsequent builds
RUN cargo fetch -p sui-types 2>/dev/null || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier
