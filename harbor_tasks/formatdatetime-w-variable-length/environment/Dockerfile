FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
ENV CC=clang-15
ENV CXX=clang++-15

# Create working directory
WORKDIR /workspace

# Clone ClickHouse repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=0ac8d1fb82e45ca6c903f5549d564e867fb422dd
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

# Pre-install python dependencies for testing
RUN pip3 install pytest pyyaml

WORKDIR /workspace/ClickHouse
