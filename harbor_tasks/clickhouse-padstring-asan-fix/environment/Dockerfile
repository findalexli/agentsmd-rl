# syntax=docker/dockerfile:1

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for ClickHouse build verification and testing
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    clang-format-15 \
    lld-15 \
    llvm-15 \
    python3 \
    python3-pip \
    python3-venv \
    ccache \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up alternatives for clang
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100 \
    && update-alternatives --install /usr/bin/clang-format clang-format /usr/bin/clang-format-15 100

# Install pytest
RUN pip3 install pytest

# Clone ClickHouse repo (sparse checkout for the files we need)
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none --sparse \
    https://github.com/ClickHouse/ClickHouse.git && \
    cd ClickHouse && \
    git sparse-checkout set src/Functions base/glibc-compatibility && \
    git fetch --depth=1 origin 6958fcb996ad34fe65d3d26d08de9cefd4788351 && \
    git checkout 6958fcb996ad34fe65d3d26d08de9cefd4788351

# Set up build directory structure and logs
RUN mkdir -p /workspace/ClickHouse/build && mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
