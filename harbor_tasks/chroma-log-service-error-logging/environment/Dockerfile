FROM rust:1.85-slim

RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

RUN mkdir -p /workspace /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git chroma \
    && cd chroma \
    && git checkout 1e76db4c961642b5fd34e888c5bf0fca754c6038

WORKDIR /workspace/chroma/rust/log-service

# Pre-build dependencies to cache them
RUN cargo fetch
