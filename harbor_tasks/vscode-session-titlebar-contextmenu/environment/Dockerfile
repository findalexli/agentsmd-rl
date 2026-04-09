FROM node:22-slim

# Install git, curl, build tools, python3 for scoring
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Base commit: parent of merge commit b730821 (VS Code PR #306419)
ENV BASE_COMMIT=6a7e1b4bd33c970a4c5275ab90dbfd6a3cb91aa0
ENV REPO_URL=https://github.com/microsoft/vscode.git

# Clone VS Code at base commit as a sanitized snapshot
RUN git clone --depth=1 "$REPO_URL" vscode && \
    cd vscode && \
    git fetch --depth=1 origin "$BASE_COMMIT" && \
    git checkout "$BASE_COMMIT" && \
    rm -rf .git && \
    git init && \
    git config user.email "test@test.com" && \
    git config user.name "Test" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies (only what's needed for TypeScript compilation)
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts --legacy-peer-deps || npm install --ignore-scripts --legacy-peer-deps

# Configure environment
ENV PATH="/workspace/vscode/node_modules/.bin:${PATH}"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/vscode
