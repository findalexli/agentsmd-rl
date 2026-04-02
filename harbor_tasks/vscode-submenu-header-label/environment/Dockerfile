FROM node:22-slim

# Install dependencies including Python for node-gyp, git, and build tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up git user for git operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone VS Code at the base commit (parent of merge commit)
WORKDIR /workspace
ARG BASE_COMMIT=29f5047784335d81e143570a307f75f7800c603a
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install npm dependencies (minimal - TypeScript only, no extensions build needed for tests)
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Sanitize: remove .git history to create snapshot
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
