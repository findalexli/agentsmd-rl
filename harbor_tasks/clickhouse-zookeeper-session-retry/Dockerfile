FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for ClickHouse build
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
    curl \
    wget \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100

# Install pytest
RUN pip3 install pytest pyyaml

# Create working directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git checkout 6f01023e78a9e84c588068560fda778a7c11a665

WORKDIR /workspace/ClickHouse
