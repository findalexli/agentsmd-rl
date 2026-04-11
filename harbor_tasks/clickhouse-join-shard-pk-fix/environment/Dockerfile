# Use Python as base since we need Python for testing
FROM python:3.12-slim

# Install build dependencies for ClickHouse
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    cmake \
    ninja-build \
    clang \
    llvm \
    lld \
    libc++-dev \
    libc++abi-dev \
    libssl-dev \
    libcrypto++-dev \
    libicu-dev \
    libxml2-dev \
    liblzma-dev \
    libz-dev \
    libbz2-dev \
    libdouble-conversion-dev \
    libpcre2-dev \
    libgoogle-perftools-dev \
    libjemalloc-dev \
    libodbc2 \
    libodbccr2 \
    libltdl7 \
    libre2-dev \
    libzstd-dev \
    liblz4-dev \
    libsnappy-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libcurl4-openssl-dev \
    libsqlite3-dev \
    rapidjson-dev \
    libmsgpack-dev \
    libboost-all-dev \
    ccache \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up ccache
ENV CCACHE_DIR=/ccache
ENV CCACHE_MAXSIZE=5G
ENV PATH="/usr/lib/ccache:$PATH"
RUN mkdir -p /ccache

# Clone ClickHouse at base commit (with minimal history for speed)
# Using --filter=blob:none to reduce download size
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git checkout f4eb1501802bc9f274870d147ae82979956939e6

# Set up build directory (optional - speeds up subsequent builds)
WORKDIR /workspace/ClickHouse
RUN mkdir -p build && cd build && \
    cmake .. \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTS=OFF \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_UTILS=OFF \
    -DENABLE_CCACHE=ON \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
    -GNinja 2>&1 | tail -20 || true

# Create verifier log directory
RUN mkdir -p /logs/verifier

# Working directory for task
WORKDIR /workspace/ClickHouse
