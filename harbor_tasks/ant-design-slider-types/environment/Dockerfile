FROM node:22-slim

# Install Python, pytest and git for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone ant-design repo at base commit
ARG BASE_COMMIT=5e6a263cfe58b7bbe428a80bf4fd0de0e359d6b7
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git && \
    cd ant-design && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ant-design

# Set NODE_OPTIONS to increase memory limit for TypeScript compilation
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Install dependencies
RUN npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier
