# ClickHouse UDF ZooKeeper Fix Task
# This is a C++ codebase, so we need a build environment

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install essential build dependencies and Python for testing
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    clang-18 \
    llvm-18 \
    lld-18 \
    cmake \
    ninja-build \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Install Python packages for testing
RUN pip3 install --break-system-packages \
    pyyaml \
    pytest \
    pytest-json-report \
    tree-sitter \
    tree-sitter-cpp

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Clone ClickHouse repository at the base commit
# Using shallow clone for speed
WORKDIR /workspace
ARG BASE_COMMIT=a3c77899d3f826cfdc879ce9c276dd5f019cb46d
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Set working directory to the repo
WORKDIR /workspace/ClickHouse
