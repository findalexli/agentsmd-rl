FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install build dependencies and Python
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
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git checkout d17f0940dc7aba89d01ed0110e04fc54e4f24ace

WORKDIR /workspace/ClickHouse
