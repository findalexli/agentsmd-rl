FROM rust:1.85-slim

# Install python3, pip, git, and build dependencies for rocksdb
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    libclang-dev \
    cmake \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone https://github.com/MystenLabs/sui.git

WORKDIR /workspace/sui
RUN git checkout 6a391733c6a07cda5d3c9939efee306490d16bd

# Install rustfmt for cargo fmt testing
RUN rustup component add rustfmt

# Pre-download dependencies to speed up builds
RUN cargo fetch -p sui-indexer-alt-framework 2>/dev/null || true

WORKDIR /workspace/sui
