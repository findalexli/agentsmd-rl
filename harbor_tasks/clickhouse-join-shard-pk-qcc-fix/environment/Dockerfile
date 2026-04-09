FROM ubuntu:24.04

# Install dependencies for ClickHouse build validation
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    llvm-18 \
    lld-18 \
    python3 \
    python3-pip \
    python3-pytest \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Create working directory
WORKDIR /workspace

# Clone ClickHouse at base commit with shallow history for faster clone
# Base commit: 63f473f503c91e0694389620a168e40c4ccc6483
RUN git clone --filter=blob:none --depth=100 \
    https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=100 origin 63f473f503c91e0694389620a168e40c4ccc6483 \
    && git checkout 63f473f503c91e0694389620a168e40c4ccc6483

# Set up directory for logs
RUN mkdir -p /logs/verifier

# Pre-install pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

WORKDIR /workspace/ClickHouse
