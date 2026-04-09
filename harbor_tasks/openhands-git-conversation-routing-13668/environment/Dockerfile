FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=df4fea6aca28d3050189a1b19d91ad3d129a95cb
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/openhands/frontend
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
