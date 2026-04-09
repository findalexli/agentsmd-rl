FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build tools, git, python3, and clang tools for C++ syntax checking
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    clang \
    clang-tools \
    cmake \
    ninja-build \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone ClickHouse repo at base commit with minimal history
# Using filter=blob:none to get a shallow clone but with full tree info
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/clickhouse && \
    cd /workspace/clickhouse && \
    git fetch --depth=1 origin 4d79f6ea35f896060e55128fe8ca4216f455d9c0 && \
    git checkout 4d79f6ea35f896060e55128fe8ca4216f455d9c0

# Install pytest for running tests
RUN pip3 install pytest pyyaml --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the clickhouse repo
WORKDIR /workspace/clickhouse
