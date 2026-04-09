FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/continuedev/continue.git && \
    cd continue && \
    git checkout a3dbeb346b4f9e7384b78c62b4f0f3074acfc42d

# Install dependencies
WORKDIR /workspace/continue
RUN npm ci 2>&1 || npm install 2>&1

# Build the core package
WORKDIR /workspace/continue/core
RUN npm ci 2>&1 || npm install 2>&1

# Build the binary package
WORKDIR /workspace/continue/binary
RUN npm ci 2>&1 || npm install 2>&1

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
