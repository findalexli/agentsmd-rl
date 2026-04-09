FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CLICKHOUSE_REPO=ClickHouse/ClickHouse
ENV BASE_COMMIT=6f01023e78a9e84c588068560fda778a7c11a665

# Install required packages for building and running Python tests
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    clang++-15 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    libssl-dev \
    libz-dev \
    liblz4-dev \
    libzstd-dev \
    libicu-dev \
    libdouble-conversion-dev \
    libgoogle-perftools-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN python3 -m pip install --upgrade pip pytest

# Create workspace
WORKDIR /workspace

# Clone ClickHouse at specific commit (shallow clone for speed)
RUN git clone --depth 100 --filter=blob:none https://github.com/${CLICKHOUSE_REPO}.git clickhouse && \
    cd clickhouse && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/clickhouse

# Set environment variables for build
ENV CC=clang-15
ENV CXX=clang++-15

# The source file is at src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
