FROM node:22-slim

# Install Python3 for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit (buggy version)
ARG REPO=https://github.com/excalidraw/excalidraw.git
ARG BASE_COMMIT=87faa5d3da055ea22c6bce261ee88087bf4cca0e

RUN git clone --filter=blob:none $REPO excalidraw && \
    cd excalidraw && \
    git checkout $BASE_COMMIT

WORKDIR /workspace/excalidraw

# Install dependencies (use yarn as the project uses yarn)
RUN yarn install --frozen-lockfile

# Pre-build packages to ensure they compile
RUN yarn build:packages || true

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
