FROM node:22-slim

# Install base dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Base commit (pre-fix)
ARG BASE_COMMIT=d7ebb2cc7dcab5b7d7c9bc98ad5b96652dcab650

# Clone VS Code at base commit (shallow clone for speed)
RUN git clone --depth=100 --branch main https://github.com/microsoft/vscode.git /workspace/vscode && \
    cd /workspace/vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize: remove .git history but keep structure for git diff
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "Base snapshot at pre-fix commit"

# Install minimal dependencies for TypeScript compilation
# Only install what's needed to validate the code compiles
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts --omit=optional 2>/dev/null || npm install --ignore-scripts --omit=optional 2>/dev/null || true

# Install TypeScript globally for compilation checks
RUN npm install -g typescript@5.5.4

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
