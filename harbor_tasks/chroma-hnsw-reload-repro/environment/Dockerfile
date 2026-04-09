FROM rust:1.85-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone chroma repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git
WORKDIR /workspace/chroma
RUN git checkout c7922d30c73dcf4b1549e2b00afe4b23b6da489d

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/chroma/rust
RUN cargo fetch

# Set working directory for the task
WORKDIR /workspace/chroma
