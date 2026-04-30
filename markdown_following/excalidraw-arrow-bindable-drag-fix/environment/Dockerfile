FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=60ab14c2f633112613843eec3c049f6da0f566e8
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git && \
    cd excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
