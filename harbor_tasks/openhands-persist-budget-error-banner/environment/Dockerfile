FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=8ce3089a68018c507025c7410ee3ba25856b23fd
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root for tests
WORKDIR /workspace/OpenHands
