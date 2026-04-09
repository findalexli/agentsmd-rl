FROM node:22-slim

# Install Python and patch for pytest runner and applying patches
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git patch \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=eba1f60c1d34ae68d34171a753d5e6b3ab5ad0be
RUN git clone --filter=blob:none --depth=50 https://github.com/All-Hands-AI/OpenHands.git openhands \
    && cd openhands \
    && git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands
