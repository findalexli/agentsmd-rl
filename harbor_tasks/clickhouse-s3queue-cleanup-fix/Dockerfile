FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    llvm-15 \
    libc++-15-dev \
    libc++abi-15-dev \
    libicu-dev \
    libssl-dev \
    libboost-all-dev \
    libzookeeper-mt-dev \
    zookeeper \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml

RUN git clone --filter=blob:none --depth=500 \
    https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse \
    && cd /workspace/ClickHouse \
    && git checkout c71831a6b0df9e6b69eaba0e4cf83801c1fb3832

WORKDIR /workspace/ClickHouse

RUN mkdir -p /logs/verifier

COPY tests/test_outputs.py /workspace/tests/
COPY task.toml /workspace/task/
COPY solve.sh /workspace/
COPY test.sh /workspace/
