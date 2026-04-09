FROM node:22-slim

# Install Python (needed by pytest runner) and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the ant-design repo at the base commit
# Use full clone to get package-lock.json for npm ci
ARG BASE_COMMIT=aa0594058b3735533a59c83feb5c309e88b544bd
RUN git clone --depth=1 https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install npm dependencies (takes time, do it early)
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/ant-design
