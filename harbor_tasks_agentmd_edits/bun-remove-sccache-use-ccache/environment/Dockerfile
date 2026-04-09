FROM ubuntu:24.04

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake ninja-build python3 python3-pip curl wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone bun repo at base commit
ARG BASE_COMMIT=5715b54614cbdb885ab42584d401c300cdff9519
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git && \
    cd bun && \
    git checkout ${BASE_COMMIT}

# Install pytest
RUN pip3 install pytest --break-system-packages || pip3 install pytest

WORKDIR /workspace/bun
