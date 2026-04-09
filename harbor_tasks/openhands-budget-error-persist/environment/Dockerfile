FROM node:22-slim

# Install Python and required tools for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create required directory for verifier
RUN mkdir -p /logs/verifier

# Clone the OpenHands repository at the base commit
# Using --filter=blob:none for sparse checkout since we only need frontend
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands

WORKDIR /workspace/openhands
# Checkout base commit (parent of merge commit)
RUN git checkout 8ce3089a68018c507025c7410ee3ba25856b23fd

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm ci

WORKDIR /workspace
