FROM node:22-slim

# Install Python for test runner and git
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace/excalidraw

# Clone the repo and checkout base commit
# Need to fetch specific commit, so we can't use --depth=1
RUN git clone --depth=1 --filter=blob:none https://github.com/excalidraw/excalidraw.git . && \
    git checkout d6f0f34fe91a7fab25106f2b31b074c132815d36

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for task execution
WORKDIR /workspace/excalidraw
