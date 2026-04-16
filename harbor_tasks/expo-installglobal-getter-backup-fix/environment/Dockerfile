FROM node:22-slim

# Install required packages including git and python3
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the expo repository at the base commit (shallow clone for efficiency)
ARG BASE_COMMIT=b2a49055ba0c009e93829edd569fbe21dabcdd2c
RUN git clone --filter=blob:none --depth=100 https://github.com/expo/expo.git && \
    cd expo && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Verify the checkout
RUN cd /workspace/expo && git log -1 --oneline

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set the working directory to the expo package
WORKDIR /workspace/expo/packages/expo

# We don't run npm install here - tests will handle dependencies via mocks
# The test file uses direct source imports with appropriate mocks
