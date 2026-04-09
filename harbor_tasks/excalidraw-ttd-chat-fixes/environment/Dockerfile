FROM node:22-slim

# Install git, python3, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Clone the repository at base commit (full clone needed for commit history)
ARG REPO=excalidraw/excalidraw
ARG BASE_COMMIT=a0b98a944f1ddedba090b8a6908ff38b9132177e
RUN git clone https://github.com/${REPO}.git excalidraw && \
    cd excalidraw && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/excalidraw
RUN yarn install --frozen-lockfile

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace
