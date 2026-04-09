FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies for ClickHouse and Python for tests
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    ccache \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest pyyaml --break-system-packages

# Clone ClickHouse at base commit (shallow clone for speed)
ARG BASE_COMMIT=2ffea49f37f25c9a09a74b9ecb338b05eb426370
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch some headers to help with syntax checking later
RUN mkdir -p /workspace/headers

# Keep container running for interactive use
CMD ["/bin/bash"]
