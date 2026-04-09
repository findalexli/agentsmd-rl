FROM rust:1.85-slim

# Install system dependencies for Sui and Python
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    clang \
    libclang-dev \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone Sui repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=b11d7b977aab3ab79dc6f783555d1726c34b6ca7
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Pre-download Rust dependencies (this layer can be cached)
WORKDIR /workspace/sui
RUN cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
