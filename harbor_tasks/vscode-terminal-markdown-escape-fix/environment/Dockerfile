# VS Code: Remove unnecessary markdown escaping in terminal invocation messages
# Base: Node.js image for TypeScript compilation
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

# Clone VS Code repo at the base commit (pre-fix)
WORKDIR /workspace
RUN git clone --depth=1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin 891f5f2f96fe5161122912af25d8b3af708cbd1b && \
    git checkout 891f5f2f96fe5161122912af25d8b3af708cbd1b

# Create sanitized snapshot (no .git history for smaller image)
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for TypeScript compilation only
# VS Code's npm install can be heavy, so we only install what's needed for type checking
WORKDIR /workspace/vscode
RUN npm install --ignore-scripts 2>&1 || true

# Set up workspace
WORKDIR /workspace/vscode
ENV NODE_ENV=development

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
