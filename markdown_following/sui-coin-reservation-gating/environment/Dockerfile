FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Rust components needed for testing
RUN rustup component add clippy rustfmt

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the Sui repository at base commit
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui
WORKDIR /workspace/sui

# Checkout the base commit (parent of merge commit)
RUN git checkout 08740a5fd4f46df33dc6dda8b34056ce9a54e3fd

# Create logs directory
RUN mkdir -p /logs/verifier

# Keep container running
CMD ["bash"]
