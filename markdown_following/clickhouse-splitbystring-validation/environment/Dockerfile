FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for ClickHouse build and Python
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for testing
RUN python3 -m pip install --break-system-packages pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo at base commit (shallow clone to save space)
WORKDIR /workspace
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin 2ffea49f37f25c9a09a74b9ecb338b05eb426370 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse
