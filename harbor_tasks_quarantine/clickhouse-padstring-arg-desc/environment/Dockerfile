FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    llvm-15 \
    libc++-15-dev \
    libc++abi-15-dev \
    build-essential \
    curl \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN pip3 install pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone ClickHouse repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=a77cd4c5a6ede8a2d5da637a75348a4cc055c007
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git && \
    cd ClickHouse && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse
