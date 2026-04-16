FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    ninja-build \
    pkg-config \
    curl \
    wget \
    file \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (needed for Bun build scripts)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

# Install pytest
RUN pip install pytest

# Create workspace
WORKDIR /workspace

# Clone Bun repo at the pre-fix commit
ARG BASE_COMMIT=995d988c736293572f0a5a2c8a49fd1a2b6ca84c
RUN git clone --filter=blob:none --depth=1 https://github.com/oven-sh/bun.git bun \
    && cd bun \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Create logs directory for Harbor
RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
