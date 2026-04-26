FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=d29fd62e417b8cb73d1d5dc3e207735046401491
RUN git init /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git remote add origin https://github.com/excalidraw/excalidraw.git && \
    git fetch --depth=1 origin d29fd62e417b8cb73d1d5dc3e207735046401491 && \
    git checkout FETCH_HEAD

# Install dependencies for testing (only what test_outputs.py needs)
RUN cd /workspace/excalidraw && \
    npm install typescript --save-dev 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/excalidraw
