FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies needed to build ClickHouse and run tests
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    python3 \
    python3-pip \
    python3-pytest \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libicu-dev \
    libreadline-dev \
    libgtest-dev \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN pip3 install --break-system-packages pyyaml requests

# Create directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

# Clone ClickHouse repo at the base commit
# NOTE: Original PR base 11943f24a8dcc6274d50136144d0078ab7a56fad was force-pushed/orphaned upstream.
# Switched to task.toml base_commit 78c08e71c93e3bd0657b54402d083f96d90d76c8 which is still reachable.
WORKDIR /workspace
ARG BASE_COMMIT=78c08e71c93e3bd0657b54402d083f96d90d76c8
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse
