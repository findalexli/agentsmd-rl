FROM rust:1.85-slim

# Install system dependencies including libclang for bindgen
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    curl \
    build-essential \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Sui repository at base commit
# Using shallow clone for faster checkout
RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git && \
    cd sui && \
    git checkout 5ce3eba9d21aea6f051be3c3306078d2bc572c41

# Pre-build to cache dependencies (optional but helps speed up)
WORKDIR /workspace/sui

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment for testing
ENV SUI_SKIP_SIMTESTS=1
ENV CARGO_NET_OFFLINE=false
ENV LIBCLANG_PATH=/usr/lib/llvm-14/lib
