FROM node:22-slim

# Install git, curl, ca-certificates, build tools, python (for tests)
RUN apt-get update && apt-get install -y     git curl ca-certificates build-essential python3 python3-pip     && rm -rf /var/lib/apt/lists/*

# Sanitized git snapshot - no .git history
WORKDIR /workspace
RUN git clone --depth=1 https://github.com/microsoft/vscode.git vscode     && cd vscode     && git fetch --depth=1 origin f8c32042ed5206d294fe73f1a3b2b74cd3f7bb7a     && git checkout f8c32042ed5206d294fe73f1a3b2b74cd3f7bb7a     && rm -rf .git     && git init     && git config user.email "agent@example.com"     && git config user.name "Agent"     && git add -A     && git commit -m "snapshot"

# Configure git (for any later operations)
WORKDIR /workspace/vscode

# Create test directories
RUN mkdir -p /logs/verifier /tests

# No npm install needed - this is a pure CSS change
# VS Code's CSS files are just static files

ENV WORKDIR=/workspace/vscode
