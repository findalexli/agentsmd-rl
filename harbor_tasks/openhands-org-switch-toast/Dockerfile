FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 30b7af31b9cc6c7e1dbdb88f311ae4da3fdfb3c3

WORKDIR /workspace/OpenHands/frontend

# Install frontend dependencies
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/task
