FROM rust:1.85-slim

# Install Python, git, and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=e6ce738cfcbbf2ceae0d86e85e8df39b3abb7213
RUN git clone --filter=blob:none --depth=100 https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Pre-download Rust dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch --locked 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set default workdir for tests
WORKDIR /workspace/sui
