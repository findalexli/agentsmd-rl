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
RUN git clone --depth=1 --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=1 origin 7dad4d8f7af43976fa63a062d20225aad04842c8 \
    && git checkout 7dad4d8f7af43976fa63a062d20225aad04842c8

WORKDIR /workspace/ClickHouse
