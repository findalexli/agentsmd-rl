FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    python3 \
    python3-pip \
    libssl-dev \
    libicu-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100

# Install pytest
RUN pip3 install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone ClickHouse at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git checkout 1dc0c61cb50c6591ce100672ec6340e72f174a58

WORKDIR /workspace/ClickHouse
