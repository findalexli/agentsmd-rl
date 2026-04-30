FROM ubuntu:22.04

# Install build tools, Python, and curl
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    clang-14 \
    clang-format-14 \
    llvm-14 \
    libc++-dev \
    libc++abi-dev \
    libboost-all-dev \
    curl \
    wget \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Clone the repository at the base commit of PR #101500
ARG BASE_COMMIT=dd28467d2e3415a439b64f8a41864c1336a2170f
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin dd28467d2e3415a439b64f8a41864c1336a2170f && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment for build
ENV CC=clang-14
ENV CXX=clang++-14
