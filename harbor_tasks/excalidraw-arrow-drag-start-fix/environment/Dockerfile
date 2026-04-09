FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /workspace/excalidraw /logs/verifier

# Clone the repo at base commit (filter=blob:none for efficiency)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw

WORKDIR /workspace/excalidraw
RUN git checkout 60ab14c2f633112613843eec3c049f6da0f566e8

# Install dependencies
RUN yarn install --frozen-lockfile

# Pre-build packages for faster test execution
RUN yarn build:packages

WORKDIR /workspace
