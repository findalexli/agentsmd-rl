FROM node:22-slim

# Install Python for pytest and basic tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit
# Use --filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git excalidraw

WORKDIR /workspace/excalidraw

# Checkout the base commit (parent of merge commit)
RUN git checkout c1e00c44f57841b18ea14bde30b8d1f5aff95c7e

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace
