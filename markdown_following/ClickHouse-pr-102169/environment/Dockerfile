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
    libclang-dev \
    libc++-dev \
    libc++abi-dev \
    build-essential \
    pkg-config \
    ripgrep \
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
WORKDIR /workspace
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin 4d79f6ea35f896060e55128fe8ca4216f455d9c0 && \
    git checkout FETCH_HEAD

# Pre-create logs directory for test results
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages codespell 2>/dev/null || pip install --no-cache-dir codespell
