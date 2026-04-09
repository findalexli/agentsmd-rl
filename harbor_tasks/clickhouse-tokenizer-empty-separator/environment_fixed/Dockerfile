# ClickHouse build environment for tokenizer validation fix
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    llvm-15 \
    lld-15 \
    python3 \
    python3-pip \
    python3-pytest \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Install newer CMake via pip (3.25+)
RUN pip3 install "cmake>=3.25"

# Create clang symlinks
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100

# Clone ClickHouse at base commit (with shallow clone for speed)
ARG BASE_COMMIT=7dad4d8f7af43976fa63a062d20225aad04842c8
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create required directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
