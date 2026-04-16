FROM node:22-slim

# Install Python3 and required dependencies for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the excalidraw repo at base commit
ARG BASE_COMMIT=063533aede8365bf18b8f08ec949a1e93697c17d
RUN git clone --filter=blob:none https://github.com/excalidraw/excalidraw.git /workspace/excalidraw \
    && cd /workspace/excalidraw \
    && git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/excalidraw
