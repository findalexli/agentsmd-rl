FROM node:22-slim

# Install Python for pytest-based verification
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=9ba0f5dbc9d551aad9277341a82449e04043c5ae
RUN git clone --depth=100 --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies (needed for TypeScript checking)
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

WORKDIR /workspace
