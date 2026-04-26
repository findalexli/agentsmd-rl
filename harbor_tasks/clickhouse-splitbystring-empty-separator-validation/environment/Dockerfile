FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    clang-15 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for test runner
RUN pip3 install pytest pyyaml

# Clone ClickHouse repository shallowly at base commit
WORKDIR /workspace
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin 4735a442e4fd8d0b317a2171945fbcaf8cfa7ec7 && \
    git checkout FETCH_HEAD

# Create logs directory
RUN mkdir -p /logs/verifier

# Default working directory
WORKDIR /workspace/ClickHouse
