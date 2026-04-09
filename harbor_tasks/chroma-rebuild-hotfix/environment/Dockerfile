FROM rust:1.85-slim

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone chroma repo at base commit
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git chroma && \
    cd chroma && \
    git checkout ab4a15df0055b65b8c2fa6e3ce1115d55ecfad22

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV REPO=/workspace/chroma
ENV RUST_BACKTRACE=1
