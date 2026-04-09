# ClickHouse C++ build environment with Python for testing
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and Python
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    python3 \
    python3-pip \
    curl \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest

# Create required directories
RUN mkdir -p /workspace /logs/verifier

# Clone ClickHouse repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=f4eb1501802bc9f274870d147ae82979956939e6
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=100 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse
