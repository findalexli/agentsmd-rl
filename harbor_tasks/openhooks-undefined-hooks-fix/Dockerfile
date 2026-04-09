FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git checkout 3cd85a07b78a2d9d2e28b2904e1b42096d47a802

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands
