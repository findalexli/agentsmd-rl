FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    llvm-18 \
    libc++-18-dev \
    libc++abi-18-dev \
    libssl-dev \
    libicu-dev \
    libxml2-dev \
    liblua5.1-dev \
    libcsv-dev \
    libboost-all-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    libzstd-dev \
    libsnappy-dev \
    libthrift-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libmysqlclient-dev \
    libpq-dev \
    libsqlite3-dev \
    librocksdb-dev \
    libcurl4-openssl-dev \
    libgtest-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for testing
RUN pip3 install pytest pyyaml --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone ClickHouse at base commit (shallow clone with filter for speed)
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git checkout 82211a574743ad08dfbe01e1252040efd544f9c5

# Create log directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
