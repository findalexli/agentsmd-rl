FROM node:22-slim

# Install Python and pip for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone mantine repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=7fbe5d8a5f3e89c57bd37c10a096812c0fc673d3
RUN git clone --filter=blob:none --depth=100 https://github.com/mantinedev/mantine.git /workspace/mantine && \
    cd /workspace/mantine && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/mantine
