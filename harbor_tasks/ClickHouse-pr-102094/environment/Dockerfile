FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up alternatives for clang
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Install pytest for test verification
RUN python3 -m pip install --break-system-packages pytest

# Create working directory
WORKDIR /workspace

# Clone ClickHouse at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git checkout 4735a442e4fd8d0b317a2171945fbcaf8cfa7ec7

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
