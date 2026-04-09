FROM rust:1.85-slim

# Install python3 for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed, but full tree for move crates)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git /workspace/sui && \
    cd /workspace/sui && \
    git checkout 8810914bd8a82363390cbd30eb12188b34592c87

# Install pytest
RUN pip3 install pytest --break-system-packages

# Setup logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
