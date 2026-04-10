FROM rust:1.85-slim

# Install dependencies: git, python3, pip, libclang
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout f8024baa75086db5a440d98247ecfd3d1ee90c73

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
