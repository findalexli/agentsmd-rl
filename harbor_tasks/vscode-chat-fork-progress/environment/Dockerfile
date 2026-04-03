FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at base commit (parent of merge commit)
# PR 306207 merge commit: b27242af3a1749bb0223224e87ec8432e825b91f
# Parent (base): 99a7b4b0842dca767b056a303efa2412edfa16d8
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin 99a7b4b0842dca767b056a303efa2412edfa16d8 && \
    git checkout 99a7b4b0842dca767b056a303efa2412edfa16d8 && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="agent@test.com" -c user.name="Agent" commit -m "snapshot"

# Install minimal TypeScript/node dependencies for type checking
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts --prefer-offline 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Configure git for tests
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Set up logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
