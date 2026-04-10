FROM rust:1.85-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    protobuf-compiler \
    libssl-dev \
    pkg-config \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Create workspace and logs directories
RUN mkdir -p /workspace/chroma /logs/verifier

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git && \
    cd chroma && \
    git checkout 2c83ca50da86f4f71d2c8b9a8ae9f17ec0ae6c20

# Pre-build dependencies to cache them
WORKDIR /workspace/chroma/rust
RUN cargo fetch

# Copy test files
RUN ln -s /tests/test_outputs.py /workspace/test_outputs.py

WORKDIR /workspace
