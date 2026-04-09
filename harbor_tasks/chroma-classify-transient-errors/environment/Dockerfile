FROM rust:1.85-slim

# Install python3 for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=e92cd203c4343bf422271146c42042dd6fa5caed
RUN git clone --filter=blob:none https://github.com/chroma-core/chroma.git chroma && \
    cd chroma && \
    git checkout ${BASE_COMMIT}

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Pre-build dependencies to speed up task execution
WORKDIR /workspace/chroma/rust
RUN cargo fetch

WORKDIR /workspace
