FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    cmake \
    ninja-build \
    clang-18 \
    llvm-18 \
    libc++-18-dev \
    libc++abi-18-dev \
    lld-18 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN pip3 install --break-system-packages pytest

# Create directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo at base commit
ARG BASE_COMMIT=a77cd4c5a6ede8a2d5da637a75348a4cc055c007
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Pre-configure to enable faster builds during testing
RUN mkdir -p build && cd build && \
    cmake .. \
    -DCMAKE_CXX_COMPILER=clang++-18 \
    -DCMAKE_C_COMPILER=clang-18 \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTS=OFF \
    -DENABLE_CLICKHOUSE_ALL=OFF \
    -DENABLE_CLICKHOUSE_SERVER=OFF \
    -DENABLE_CLICKHOUSE_CLIENT=OFF \
    -DENABLE_CLICKHOUSE_LOCAL=OFF \
    2>&1 | head -50 || true

# Set environment
ENV CC=clang-18
ENV CXX=clang++-18
