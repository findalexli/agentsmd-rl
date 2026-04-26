FROM node:22-slim

# Install dependencies for running validation
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install bun for validation
RUN npm install -g bun

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/bun

# Clone the Bun repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=a14a89ca953910e89697895dfdfb4cdf4c90a151
RUN git init /workspace/. && \
    cd /workspace/. && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin a14a89ca953910e89697895dfdfb4cdf4c90a151 && \
    git checkout FETCH_HEAD

# Install minimal dependencies for validation
RUN bun install --frozen-lockfile || npm install

# Pre-install Python dependencies for testing
RUN pip3 install pytest --break-system-packages
