# Rust environment for sui-framework tests
FROM rust:1.85-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install --break-system-packages pytest pyyaml

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 2409c793c8f6092d665d28030cfc68967e5fc4dd

# Create log directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
