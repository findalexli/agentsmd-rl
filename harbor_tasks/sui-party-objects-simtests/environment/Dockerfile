FROM rust:1.85-slim

# Install dependencies: git, python3, pip, and other build essentials
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    curl \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at the base commit
# Using --filter=blob:none for faster clone (sparse checkout)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui \
    && cd /workspace/sui \
    && git checkout 9ca3d0f12bf261aab327bd14dfa060bd14495c9f

# Install Rust components needed for the project
RUN rustup component add rustfmt clippy

# Pre-download dependencies to speed up subsequent builds
RUN cd /workspace/sui && cargo fetch

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
