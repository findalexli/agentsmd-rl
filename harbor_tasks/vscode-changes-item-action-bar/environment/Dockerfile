FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at the pre-fix commit (d919f292bffcc695c5b23b12708c3a2ce3693f2a)
RUN git clone --depth=1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin d919f292bffcc695c5b23b12708c3a2ce3693f2a && \
    git checkout d919f292bffcc695c5b23b12708c3a2ce3693f2a

# Sanitize git history (snapshot only)
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "dev@example.com" && \
    git config user.name "Developer"

# Install npm dependencies (minimal - just for type checking)
RUN cd /workspace/vscode && npm ci --legacy-peer-deps 2>&1 | tail -20 || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set workdir
WORKDIR /workspace/vscode

# Configure git
RUN git config --global user.email "dev@example.com" && \
    git config --global user.name "Developer"
