# ClickHouse is a C++ project - use ubuntu for build environment
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone ClickHouse repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=dd28467d2e3415a439b64f8a41864c1336a2170f
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse
