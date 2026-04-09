FROM rust:1.85-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone the repo with minimal history
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 192a628cc56fcd901af4330d91c123fe8f493187

# Pre-build dependencies for faster testing (optional but helpful)
RUN cd /workspace/sui && \
    cargo fetch 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/sui
