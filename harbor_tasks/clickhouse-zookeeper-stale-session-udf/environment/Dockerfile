FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and tools
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    llvm-15 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    ca-certificates \
    pkg-config \
    libssl-dev \
    libicu-dev \
    libzookeeper-mt-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
ENV CC=clang-15
ENV CXX=clang++-15

# Clone ClickHouse repository at base commit (shallow clone for speed)
WORKDIR /workspace
ARG BASE_COMMIT=6f01023e78a9e84c588068560fda778a7c11a665
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git clickhouse \
    && cd clickhouse \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/clickhouse
