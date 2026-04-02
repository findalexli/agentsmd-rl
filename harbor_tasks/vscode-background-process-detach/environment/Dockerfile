FROM node:22-slim

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt-lists/*

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone VS Code at base commit (pre-fix)
ARG BASE_COMMIT=a4855ab045eb06a0fbe50c1a91f5ff53b4cc990b
RUN git clone https://github.com/microsoft/vscode.git vscode --depth=1 && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/vscode

# Sanitize snapshot - remove git history and create fresh init
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies needed for Node.js/TypeScript compilation
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Verify we have the expected files
RUN ls -la src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/
