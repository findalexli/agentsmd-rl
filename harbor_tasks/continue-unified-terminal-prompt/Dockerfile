FROM node:22-slim

# Install Python for pytest and basic utilities
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/continuedev/continue.git && \
    cd continue && \
    git checkout af4383f6df877ef12ba9678adec5d27b0d8e9eb3

# Install dependencies for the GUI package
WORKDIR /workspace/continue/gui
RUN npm install

WORKDIR /workspace
