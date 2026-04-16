FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    clang-format-15 \
    llvm-15 \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libicu-dev \
    libreadline-dev \
    libgmp-dev \
    libmpfr-dev \
    libboost-all-dev \
    zlib1g-dev \
    liblz4-dev \
    libzstd-dev \
    libpoco-dev \
    libjemalloc-dev \
    ragel \
    && rm -rf /var/lib/apt/lists/*

# Set up alternatives for clang
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-15 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-15 100 \
    && update-alternatives --install /usr/bin/clang-format clang-format /usr/bin/clang-format-15 100

# Set environment variables
ENV CC=clang
ENV CXX=clang++
ENV CMAKE_GENERATOR=Ninja

# Create workspace
WORKDIR /workspace

# Clone ClickHouse at the base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git \
    && cd ClickHouse \
    && git fetch --depth=100 origin f6d41a8d988b0f7cdb811e7c60b97c327677e493 \
    && git checkout f6d41a8d988b0f7cdb811e7c60b97c327677e493

# Set working directory
WORKDIR /workspace/ClickHouse

# Create build directory and configure (minimal configuration for fast compile checks)
RUN mkdir -p build \
    && cd build \
    && cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTS=OFF \
    -DENABLE_UTILS=OFF \
    -DENABLE_LIBRARIES=OFF \
    -DENABLE_SSL=OFF \
    -DENABLE_OPENSSL=OFF \
    -DENABLE_Poco_NetSSL=OFF \
    -DENABLE_Poco_Crypto=OFF \
    -DENABLE_KAFKA=OFF \
    -DENABLE_AMQPCPP=OFF \
    -DENABLE_NATS=OFF \
    -DENABLE_NURAFT=OFF \
    -DENABLE_LIBPQXX=OFF \
    -DENABLE_ODBC=OFF \
    -DENABLE_CLICKHOUSE_ODBC_BRIDGE=OFF \
    -DENABLE_RUST=OFF \
    -DENABLE_CURL=OFF \
    -DENABLE_AWS_S3=OFF \
    -DENABLE_SENTRY=OFF \
    -DENABLE_JEMALLOC=OFF \
    -DENABLE_ORC=OFF \
    -DENABLE_PARQUET=OFF \
    -DENABLE_ARROW=OFF \
    -DENABLE_AVRO=OFF \
    -DENABLE_ROCKSDB=OFF \
    -DENABLE_SNAPPY=OFF \
    -DENABLE_PROTOBUF=OFF \
    -DENABLE_THRIFT=OFF \
    -DENABLE_CASSANDRA=OFF \
    -DENABLE_YAML_CPP=OFF \
    -DENABLE_BROTLI=OFF \
    -DENABLE_BZIP2=OFF \
    -DENABLE_FASTFLOAT=OFF \
    -DENABLE_PDQ_SORT=OFF \
    -DENABLE_SQLITE=OFF \
    -DENABLE_ZLIB=OFF \
    -DENABLE_LZ4=OFF \
    -DENABLE_ZSTD=OFF \
    2>&1 | tail -20 || echo "CMake configuration completed (may have warnings)"

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
