FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone VS Code at base commit (pre-fix)
WORKDIR /workspace
RUN git clone --no-checkout https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin dfd3b4dcb3884a3de67abfa72adfb54ba462797d && \
    git checkout dfd3b4dcb3884a3de67abfa72adfb54ba462797d

WORKDIR /workspace/vscode

# Sanitized snapshot: remove history, keep only source
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for TypeScript checking
RUN npm ci --legacy-peer-deps --ignore-scripts 2>/dev/null || npm install --legacy-peer-deps --ignore-scripts

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
