FROM ubuntu:22.04

# Install build tools, Python, and curl
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    clang-14 \
    llvm-14 \
    libc++-dev \
    libc++abi-dev \
    libboost-all-dev \
    curl \
    wget \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Clone the repository at base commit with minimal history
ARG BASE_COMMIT=d7c936ef1d4d82e0a33ab84a78f6a544a99846df
RUN git clone --depth=1 --single-branch --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment for build
ENV CC=clang-14
ENV CXX=clang++-14
