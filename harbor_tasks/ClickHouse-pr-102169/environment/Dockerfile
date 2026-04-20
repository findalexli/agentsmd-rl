# ClickHouse UDF ZooKeeper Session Fix - Task Environment
# This is a C++ codebase requiring clang-based build tools

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies for ClickHouse
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    clang-format-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    ca-certificates \
    # For AST parsing in tests
    libclang-dev \
    # C++ standard library
    libc++-dev \
    libc++abi-dev \
    # Build essentials
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for clang tools
RUN ln -sf /usr/bin/clang-18 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-18 /usr/bin/clang++ && \
    ln -sf /usr/bin/clang-format-18 /usr/bin/clang-format && \
    ln -sf /usr/bin/lld-18 /usr/bin/lld && \
    ln -sf /usr/bin/llvm-ar-18 /usr/bin/llvm-ar

# Set up Python for pytest
RUN python3 -m pip install --break-system-packages \
    pytest \
    libclang \
    pyyaml \
    subprocess-tee

# Clone ClickHouse at the base commit - shallow clone for space efficiency
# Use single branch to minimize download
WORKDIR /workspace
RUN git clone --depth=1 --single-branch --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git fetch --depth=1 origin 6d03f28ada8b3c521b504f43e04d05c915be3d75 && \
    git checkout 6d03f28ada8b3c521b504f43e04d05c915be3d75 && \
    rm -rf .git/objects/pack/*.pack .git/objects/pack/*.idx

# Pre-create logs directory for test results
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
