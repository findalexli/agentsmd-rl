FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the OpenHands repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 0b935669f35dff09303f42daf3e39c4cbb2678ed

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
