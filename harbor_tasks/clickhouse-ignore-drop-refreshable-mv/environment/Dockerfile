FROM ubuntu:24.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    clang-18 \
    clang-tidy-18 \
    llvm-18 \
    cmake \
    ninja-build \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for clang tools
RUN ln -sf /usr/bin/clang-18 /usr/bin/clang && \
    ln -sf /usr/bin/clang-tidy-18 /usr/bin/clang-tidy && \
    ln -sf /usr/bin/llvm-config-18 /usr/bin/llvm-config

# Clone ClickHouse repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git && \
    cd ClickHouse && \
    git checkout 32310ea30010c92c101d7e93c535c6bd17057dcf

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
