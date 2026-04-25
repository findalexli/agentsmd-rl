FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for test runner
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/cline/cline.git && \
    cd cline && \
    git checkout bb4e397a5131ecec15fce89da9aab7103fb84b02

# Setup CLI directory and install dependencies
WORKDIR /workspace/cline/cli

# Install dependencies
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/cline
