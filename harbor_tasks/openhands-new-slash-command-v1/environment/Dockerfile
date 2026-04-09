FROM node:22-slim

# Install git and python3 (needed by test runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=c7190ddb308de5a8c00b790049c5027d122159f7
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir is the frontend directory
WORKDIR /workspace/OpenHands/frontend
