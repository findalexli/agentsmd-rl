FROM rust:1.85-slim

# Install Python and other required dependencies including build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    libssl-dev \
    clang \
    libclang-dev \
    llvm-dev \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set libclang path for bindgen
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib

# Set up Python environment for pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the sui repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 21a5ae30270cc67b3e331d7beb342be2d19c7e97

WORKDIR /workspace/sui

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies to speed up builds (this may take a while)
RUN cargo fetch || true

# Default command
CMD ["bash"]
