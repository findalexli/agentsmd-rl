FROM rust:1.85-slim-bookworm

# Install dependencies: git, python3 (for pytest), and build tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory and logs directory
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the Sui repository at the base commit (shallow clone for speed)
ARG BASE_COMMIT=ceb0bf788b8711eca37a448854db0421beb8d612
RUN git clone --filter=blob:none --no-checkout https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout ${BASE_COMMIT}

# Pre-fetch dependencies to speed up builds
WORKDIR /workspace/sui
RUN cargo fetch 2>&1 || true

# Default workdir for task execution
WORKDIR /workspace/sui
