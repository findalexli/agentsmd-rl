# ClickHouse C++ build environment with Python for testing
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and Python
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-15 \
    lld-15 \
    python3 \
    python3-pip \
    curl \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# Set up Python for pytest
RUN pip3 install pytest

# Create required directories
RUN mkdir -p /workspace /logs/verifier

# Clone ClickHouse repo at base commit (the state the agent must fix)
WORKDIR /workspace
ARG BASE_COMMIT=f4eb1501802bc9f274870d147ae82979956939e6
ARG MERGE_COMMIT=5f35e27d1a1192a54aabe56b74664bc8452f71ec
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout FETCH_HEAD && \
    git fetch --depth=1 origin $MERGE_COMMIT && \
    mkdir -p tests/queries/0_stateless && \
    git show $MERGE_COMMIT:tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql > tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.sql && \
    git show $MERGE_COMMIT:tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.reference > tests/queries/0_stateless/04065_join_shard_by_pk_with_qcc.reference

WORKDIR /workspace/ClickHouse
