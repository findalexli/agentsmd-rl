FROM node:22-slim

# Install Python 3 and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at the base commit (parent of merge commit)
# Using --filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw

WORKDIR /workspace/excalidraw

# Checkout the base commit
RUN git checkout 83d3943cd0973aa2fe6dc843a730bcb50e8a26ec

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir for tests
WORKDIR /workspace/excalidraw
