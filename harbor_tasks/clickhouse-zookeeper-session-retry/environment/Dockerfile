FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    llvm-18 \
    libc++-18-dev \
    libc++abi-18-dev \
    lld-18 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone ClickHouse repo at base commit
ARG BASE_COMMIT=6f01023e78a9e84c588068560fda778a7c11a665
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Install Python deps for testing
RUN pip install pytest pyyaml

# Create logs directory
RUN mkdir -p /logs/verifier
