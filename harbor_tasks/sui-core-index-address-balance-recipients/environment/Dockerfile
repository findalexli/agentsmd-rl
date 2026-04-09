FROM rust:1.85-slim

# Install Python and minimal dependencies needed for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    make \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone the Sui repository at base commit with shallow history for speed
RUN git clone --depth 1000 https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 82942c59ebb94f4f4c8ae494fed945e5f8eb4ee5

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
