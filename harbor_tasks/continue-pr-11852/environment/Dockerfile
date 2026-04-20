FROM node:20-slim

# Install python, pip, and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install --break-system-packages pytest==8.3.4

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/continuedev/continue.git continue

WORKDIR /workspace/continue

# Checkout to base commit
RUN git checkout b7fead504e7cc07b5a7b5152a2de1428e07a93fc

# Install core dependencies
WORKDIR /workspace/continue/core
RUN npm install --legacy-peer-deps 2>&1 | tail -5

# Create logs directory
RUN mkdir -p /logs/verifier