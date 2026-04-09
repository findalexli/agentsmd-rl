FROM node:22-slim

# Install Python for pytest and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip python3-pytest python3-venv \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit
ARG BASE_COMMIT=dfdd994dbbefc0562c0c5e42f267f23ae8d9d62d
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Build the math package
RUN yarn workspace @excalidraw/math build:esm

WORKDIR /workspace
