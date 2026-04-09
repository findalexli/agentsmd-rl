FROM python:3.12-slim

# Install git, patch, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Clone ClickHouse repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=4bf498e9ee91f246ff50126e3f49427ab97c7dc3
RUN git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse \
    && cd ClickHouse \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install pytest for running tests
RUN pip install --no-cache-dir pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
