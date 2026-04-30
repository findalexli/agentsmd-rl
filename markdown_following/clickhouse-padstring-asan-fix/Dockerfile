# syntax=docker/dockerfile:1

FROM ubuntu:22.04

# Install dependencies for ClickHouse build and testing
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
    ccache \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up alternatives for clang
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100

# Create working directory
WORKDIR /workspace

# Clone ClickHouse repo (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none --no-checkout https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git sparse-checkout init --cone \
    && git checkout ${BASE_COMMIT}

# Set up build directory structure (will be populated at runtime)
RUN mkdir -p /workspace/ClickHouse/build && mkdir -p /logs/verifier

# Install pytest and other Python dependencies for test runner
RUN pip3 install pytest

WORKDIR /workspace/ClickHouse
