# Use Node.js 22 (slim) as base for frontend testing
FROM node:22-slim

# Install Python for pytest test runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip3 install pytest --break-system-packages

# Set up working directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit (parent of merge)
# Using sparse checkout to reduce clone time - we only need frontend directory
ARG BASE_COMMIT=c7190ddb308de5a8c00b790049c5027d122159f7
RUN git clone --filter=blob:none --no-checkout https://github.com/OpenHands/OpenHands.git /workspace/OpenHands && \
    cd /workspace/OpenHands && \
    git sparse-checkout init --cone && \
    git sparse-checkout set frontend && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm ci

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/OpenHands/frontend
