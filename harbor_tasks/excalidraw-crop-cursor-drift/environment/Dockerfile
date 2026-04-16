FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at base commit
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw \
    && cd /workspace/excalidraw \
    && git checkout b57f3e009694acaa73e83ab9bab9a1470dd52ab3

# Install dependencies (needed for TypeScript checking)
WORKDIR /workspace/excalidraw
RUN npm install --legacy-peer-deps || npm install --force

WORKDIR /workspace
