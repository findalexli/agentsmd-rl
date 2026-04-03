FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at base commit
ARG BASE_COMMIT=f91019e7676ab34ef03e1ccb550a7a6c949fa4cd
RUN git clone --depth 1 --no-checkout https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/vscode

# Create sanitized snapshot (remove .git, re-init)
RUN rm -rf .git && \
    git init && \
    git config user.name "Test" && \
    git config user.email "test@example.com" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for testing
RUN npm install --ignore-scripts 2>/dev/null || true

# Set up logs directory
RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV CI=1
WORKDIR /workspace/vscode
