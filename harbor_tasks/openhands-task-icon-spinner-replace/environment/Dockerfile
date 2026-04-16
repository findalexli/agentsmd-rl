FROM node:22-slim

# Install git, python3 (for pytest), and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone OpenHands repo at base commit (before the fix)
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout ed5ab11fccd75b5b98c9f51ebc536713dc519275

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
