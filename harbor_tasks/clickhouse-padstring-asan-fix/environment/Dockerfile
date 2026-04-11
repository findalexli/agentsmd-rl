# syntax=docker/dockerfile:1

FROM ubuntu:22.04

# Install dependencies for ClickHouse build and testing
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

# Create working directory and repo structure
WORKDIR /workspace/ClickHouse
ARG BASE_COMMIT

# Download just the files we need from the base commit
RUN mkdir -p src/Functions base \
    && curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/${BASE_COMMIT}/src/Functions/padString.cpp" -o src/Functions/padString.cpp \
    && curl -sL "https://raw.githubusercontent.com/ClickHouse/ClickHouse/${BASE_COMMIT}/.clang-format" -o .clang-format 2>/dev/null || echo "No .clang-format"

# Create minimal base headers needed for syntax checking
RUN mkdir -p base/glibc-compatibility \
    && touch base/glibc-compatibility/empty.h

# Set up build directory structure
RUN mkdir -p /workspace/ClickHouse/build && mkdir -p /logs/verifier

# Install pytest
RUN pip3 install pytest

WORKDIR /workspace/ClickHouse
