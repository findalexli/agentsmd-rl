FROM node:22-slim

# Install python3, pip, and pytest for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 5528b01c186958bf2c92d9adaaa7f7ea0c487185

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Ensure /logs/verifier exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
