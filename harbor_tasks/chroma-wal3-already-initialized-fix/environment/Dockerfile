FROM rust:1.85-slim

# Install dependencies: git, python3, protobuf compiler, and build tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    libprotobuf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone the repository at the base commit
# Using --filter=blob:none to reduce clone size while keeping file contents accessible
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git chroma

WORKDIR /workspace/chroma

# Checkout the base commit (parent of the merge commit)
RUN git checkout caa2934cf23a9d71cd2a80dfb3989c2f028474c2

# Initialize git submodules if any
RUN git submodule update --init --recursive || true

# Pre-fetch workspace dependencies to speed up builds
# First, just fetch metadata without building
RUN cargo fetch 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
