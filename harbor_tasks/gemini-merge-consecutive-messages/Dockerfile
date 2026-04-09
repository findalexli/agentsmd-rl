FROM node:22-slim

# Install Python and required dependencies for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=d6259a73046775d90e2440117ee05cc439f26d04
RUN git clone --depth=100 --filter=blob:none https://github.com/continuedev/continue.git && \
    cd continue && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies for the packages we need to test
WORKDIR /workspace/continue/packages/openai-adapters
RUN npm install

# Also install dependencies for the core package
WORKDIR /workspace/continue/core
RUN npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set final working directory
WORKDIR /workspace
