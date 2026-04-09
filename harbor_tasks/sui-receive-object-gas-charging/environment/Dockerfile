FROM rust:1.85-slim-bookworm

# Install dependencies: git, python3, and tools for building
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at the base commit (shallow clone for speed)
# Using depth=500 to ensure we have enough history to checkout the base commit
ARG BASE_COMMIT=a6d32d34bb8e01047eca44e9e62001639090b9a7
RUN git clone --depth=500 --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Pre-download Rust dependencies to speed up builds
RUN cd /workspace/sui && cargo fetch

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
