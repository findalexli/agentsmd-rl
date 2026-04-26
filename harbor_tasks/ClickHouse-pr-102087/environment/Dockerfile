FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies needed to build ClickHouse and run tests
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    clang-18 \
    lld-18 \
    python3 \
    python3-pip \
    python3-pytest \
    curl \
    wget \
    pkg-config \
    libssl-dev \
    libicu-dev \
    libreadline-dev \
    libgtest-dev \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Set up Python (pinned deps so tests need no network)
RUN pip3 install --break-system-packages --ignore-installed \
    pyyaml==6.0.2 \
    requests==2.32.3 \
    pytest==8.3.3

# Create directories
RUN mkdir -p /workspace/ClickHouse /logs/verifier

# Clone ClickHouse repo at the base commit
WORKDIR /workspace
ARG BASE_COMMIT=78c08e71c93e3bd0657b54402d083f96d90d76c8
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin 78c08e71c93e3bd0657b54402d083f96d90d76c8 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse
