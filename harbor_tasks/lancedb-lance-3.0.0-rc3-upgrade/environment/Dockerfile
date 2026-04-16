FROM rust:1.91-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Clone lancedb repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git && \
    cd lancedb && \
    git checkout 4be85444f0c00279920c0fe6ecbee0b6918e38c1

WORKDIR /workspace/lancedb

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
