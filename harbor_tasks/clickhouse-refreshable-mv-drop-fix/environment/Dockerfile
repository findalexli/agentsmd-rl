# Task: clickhouse-refreshable-mv-drop-fix
# Fix for not ignoring DROP queries for refreshable materialized views in stress tests

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    curl \
    clang-18 \
    llvm-18 \
    llvm-18-dev \
    lld-18 \
    cmake \
    ninja-build \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for testing
RUN pip3 install --break-system-packages pyyaml

# Clone ClickHouse repository at base commit
WORKDIR /workspace
ARG BASE_COMMIT=a2c44f8d389407d145ee19293cb03d672df6dacf
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
