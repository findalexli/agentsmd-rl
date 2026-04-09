FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    llvm-15 \
    python3 \
    python3-pip \
    curl \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip3 install pytest pyyaml

# Set up working directory
WORKDIR /workspace

# Clone ClickHouse repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=2238cb4115b7215be35fe15b22b70559ea82f14c
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git /workspace/clickhouse && \
    cd /workspace/clickhouse && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/clickhouse
