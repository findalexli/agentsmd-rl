FROM ubuntu:24.04

# Install dependencies for ClickHouse build and Python
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up clang as default
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory and logs directory
WORKDIR /workspace/ClickHouse
RUN mkdir -p /logs/verifier

# Clone ClickHouse repo at base commit (shallow clone for speed)
# Base commit: ac01e7e5223a05f2a77ba74cdd949232d9648918
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && git checkout ac01e7e5223a05f2a77ba74cdd949232d9648918

# The repo will be at the base commit (buggy state)
# Tests will verify the fix is applied correctly
