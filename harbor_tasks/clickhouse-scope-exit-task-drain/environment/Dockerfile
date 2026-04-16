FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential build tools and dependencies for code checking
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    clang-15 \
    llvm-15 \
    ninja-build \
    python3 \
    python3-pip \
    curl \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
ENV CC=/usr/bin/clang-15
ENV CXX=/usr/bin/clang++-15

# Install pytest for test runner
RUN pip3 install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo at base commit (shallow clone for efficiency)
ARG BASE_COMMIT=0c2c314bd89908fc1e1073bba304895c85d488e8
WORKDIR /workspace
RUN git clone --depth 100 --filter=blob:none https://github.com/ClickHouse/ClickHouse.git clickhouse \
    && cd clickhouse \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/clickhouse
