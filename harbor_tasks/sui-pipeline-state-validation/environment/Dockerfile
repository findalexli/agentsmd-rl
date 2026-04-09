FROM rust:1.85-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    pkg-config \
    libssl-dev \
    libclang-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the Sui repository at the base commit (shallow clone for speed)
ARG BASE_COMMIT=f8024baa75086db5a440d98247ecfd3d1ee90c73
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/sui

# Build only the dependencies of the target crate first (for caching)
RUN cargo fetch -p sui-indexer-alt-framework 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
