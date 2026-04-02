FROM node:22-slim

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# VS Code specific dependencies
RUN apt-get update && apt-get install -y \
    libx11-xcb1 libxcb-dri3-0 libxtst6 libnss3 libatk-bridge2.0-0 \
    libgtk-3-0 libxss1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at base commit (shallow clone for speed)
ARG BASE_COMMIT=39a50d8d3f4cb82f8d23f6ed762d8feda0a8032f
RUN git clone --depth=1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/vscode

# Sanitized snapshot (no .git history) - keep only source at this commit
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot at base commit"

# Create logs directory
RUN mkdir -p /logs/verifier

# Install minimal dependencies for linting/type-checking
# Install only what's needed for testing (no full build)
RUN npm install --ignore-scripts 2>/dev/null || npm install --legacy-peer-deps --ignore-scripts 2>/dev/null || true

WORKDIR /workspace/vscode
