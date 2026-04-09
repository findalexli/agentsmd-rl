FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none --no-checkout https://github.com/excalidraw/excalidraw.git excalidraw && \
    cd excalidraw && \
    git sparse-checkout init && \
    git sparse-checkout set packages/excalidraw/clipboard.ts packages/excalidraw/components/FilledButton.scss packages/common/src/constants.ts && \
    git checkout ${BASE_COMMIT}

# Install dependencies for testing (only what test_outputs.py needs)
RUN cd /workspace/excalidraw && \
    npm install typescript --save-dev 2>/dev/null || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/excalidraw
