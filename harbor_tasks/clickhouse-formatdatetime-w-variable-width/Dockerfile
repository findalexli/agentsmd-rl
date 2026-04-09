FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    git \
    clang-18 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* /var/tmp/*

# Set up clang as default
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-18 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Create directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone ClickHouse repository - shallow clone with only the specific file we need
ARG BASE_COMMIT=5f9ad2e74f03897717d3940b6e22bafda9900375
RUN git clone --depth 1 --single-branch --no-checkout https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git fetch --depth 1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} -- src/Functions/formatDateTime.cpp && \
    git checkout ${BASE_COMMIT} -- .gitignore && \
    cd .. && \
    rm -rf ClickHouse/.git/objects/pack/*

WORKDIR /workspace/ClickHouse
