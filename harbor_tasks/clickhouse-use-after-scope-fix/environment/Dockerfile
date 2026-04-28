FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    llvm-18 \
    lld-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libcrypto++-dev \
    libboost-all-dev \
    libdouble-conversion-dev \
    libgtest-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default compiler
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone ClickHouse repository at base commit
# Using shallow clone for faster checkout
ARG BASE_COMMIT=cafce4334d43cfade5382a9bde6910e787d69437
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin cafce4334d43cfade5382a9bde6910e787d69437 && \
    git checkout FETCH_HEAD

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
