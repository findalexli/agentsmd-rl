FROM rust:1.85-slim

# Install system dependencies (libclang needed for sui-network build)
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    libclang-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui
WORKDIR /workspace/sui
RUN git checkout 137b12f337d790dcae827caa3dbbd56d22732716

# Create logs directory
RUN mkdir -p /logs/verifier

# Set longer timeout for cargo
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true
