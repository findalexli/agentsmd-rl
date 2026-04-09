FROM ubuntu:24.04

# Install dependencies for ClickHouse build and testing
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    clang-18 \
    llvm-18 \
    ninja-build \
    python3 \
    python3-pip \
    curl \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up python for pytest
RUN pip3 install pytest --break-system-packages

# Clone ClickHouse repo at base commit (shallow clone for speed)
WORKDIR /workspace
ARG BASE_COMMIT=97e4a1a630071d7b2ec74b2639d0d6727f8034c9
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
