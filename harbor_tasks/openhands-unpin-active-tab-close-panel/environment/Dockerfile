FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=50 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 6dd9046ba29f5d22b045a28d7a34c9ecfc981eab

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
