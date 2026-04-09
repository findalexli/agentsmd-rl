FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    python3 \
    python3-pip \
    python3-pytest \
    ccache \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libboost-all-dev \
    libpoco-dev \
    liblz4-dev \
    libzstd-dev \
    libcurl4-openssl-dev \
    libre2-dev \
    libfmt-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone ClickHouse at base commit (shallow clone for speed)
ARG REPO_URL=https://github.com/ClickHouse/ClickHouse.git
ARG BASE_COMMIT=172e4255c5cba41c87722d66c33f459256d56ce7

WORKDIR /workspace
RUN git clone --filter=blob:none --depth=1000 --branch master ${REPO_URL} ClickHouse && \
    cd ClickHouse && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ClickHouse

# Pre-install cmake dependencies for faster subsequent builds
RUN mkdir -p build && cd build && \
    cmake .. \
    -DCMAKE_C_COMPILER=clang-18 \
    -DCMAKE_CXX_COMPILER=clang++-18 \
    -DENABLE_LIBRARIES=OFF \
    -DENABLE_TESTS=OFF \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -G Ninja 2>&1 | head -100 || true
