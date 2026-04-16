FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget ca-certificates \
    python3 python3-pip python3-venv \
    cmake ninja-build \
    ccache \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (needed for bun build scripts)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone bun repo at base commit (pre-fix state)
ARG BASE_COMMIT=08e03814e56a493571da07e5d5160280e89856cd
RUN git clone --filter=blob:none --depth=1 https://github.com/oven-sh/bun.git bun && \
    cd bun && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/bun

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages || pip3 install pytest

# Copy test files will be mounted at test time
