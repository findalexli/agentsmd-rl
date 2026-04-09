FROM rust:1.85-slim

# Install system dependencies and Python for pytest runner
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/sui

# Clone the Sui repo at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git . && \
    git checkout 63cb7f767409e0589a9d5265e55a727cb8a020b5

# Install Python pytest
RUN pip3 install pytest --break-system-packages

# Pre-install Rust toolchain components needed for this crate
RUN rustup component add rustfmt clippy

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Keep container running
CMD ["sleep", "infinity"]
