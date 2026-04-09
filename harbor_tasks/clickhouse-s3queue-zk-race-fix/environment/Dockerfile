FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and python3 for pytest
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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up python for pytest
RUN pip3 install pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
