FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repo at the base commit (parent of merge commit)
# Base commit: 78833cb4077e53e0dc0e67e3382a8a1d777936db
RUN git clone --filter=blob:none https://github.com/reduxjs/redux-toolkit.git && \
    cd redux-toolkit && \
    git checkout 78833cb4077e53e0dc0e67e3382a8a1d777936db

WORKDIR /workspace/redux-toolkit

# Enable Corepack for Yarn 4.4.1
RUN corepack enable && corepack prepare yarn@4.4.1 --activate

# Install dependencies (only for toolkit package to save time)
RUN yarn install --immutable

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
