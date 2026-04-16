FROM node:22-slim

# Install Python for test harness and git for clone
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone with shallow history for faster build
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design

WORKDIR /workspace/ant-design

# Checkout the base commit (before the fix)
RUN git checkout b836ec3cc69a6ed64eb8d9e469790b424e5100cf

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
