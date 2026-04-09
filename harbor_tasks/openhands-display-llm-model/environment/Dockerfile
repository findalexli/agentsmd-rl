FROM node:22-slim

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the OpenHands repository at the base commit
# Using --depth to limit history since this is a large repo
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=100 \
    https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git fetch --depth=100 origin 0a9570eea22ca0f42dbd055d03d146375853c56c && \
    git checkout 0a9570eea22ca0f42dbd055d03d146375853c56c

WORKDIR /workspace/OpenHands

# Install frontend dependencies
RUN cd frontend && npm install

# Install backend Python dependencies (minimal for testing)
RUN pip3 install --break-system-packages pytest pyyaml dataclasses

WORKDIR /workspace/OpenHands
