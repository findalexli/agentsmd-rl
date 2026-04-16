FROM rust:1.85-slim

# Install Python for pytest and necessary tools
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

# Clone oxc repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=012c924a046b2dc14c0f381b188743fc24226b79
RUN git clone --filter=blob:none --depth=100 https://github.com/oxc-project/oxc.git && \
    cd oxc && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/oxc

# Pre-install cargo tools for ast_tools if needed
RUN cargo install cargo-run-script 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
