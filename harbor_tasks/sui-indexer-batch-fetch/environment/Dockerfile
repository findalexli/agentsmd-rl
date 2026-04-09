FROM rust:1.85-slim

# Install dependencies: git, python3, pip for pytest, protobuf compiler, and clang for bindgen
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    libclang-dev \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Set LIBCLANG_PATH for bindgen
ENV LIBCLANG_PATH=/usr/lib/x86_64-linux-gnu

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the Sui repository at base commit (shallow clone for speed)
ENV REPO_DIR=/workspace/sui
ENV BASE_COMMIT=2aaedb4930089a7ba741b246a3f8377303267351

RUN git clone --filter=blob:none https://github.com/MystenLabs/sui.git ${REPO_DIR}
WORKDIR ${REPO_DIR}

# Checkout base commit
RUN git checkout ${BASE_COMMIT}

# Pre-fetch dependencies to speed up builds
RUN cargo fetch

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR ${REPO_DIR}
