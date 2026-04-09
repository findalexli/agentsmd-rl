FROM rust:1.85-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --depth 100 --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git fetch --depth 100 origin ffbf699bc89e0d16fbcdefdd9d459b1ca0ddb88a && \
    git checkout ffbf699bc89e0d16fbcdefdd9d459b1ca0ddb88a

# Pre-download dependencies to speed up testing
WORKDIR /workspace/sui
RUN cargo fetch -p sui-indexer-alt-object-store 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace
