FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit
# Using shallow clone for efficiency
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 0b935669f35dff09303f42daf3e39c4cbb2678ed

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/OpenHands
