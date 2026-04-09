FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Clone the Sui repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 5eec71f40c7351652e51cd5200782378201f6225

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
