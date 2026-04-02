FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Configure git user for snapshot
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace

# Clone VS Code at the pre-fix commit (base commit)
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin d11c632ba8e972176f1bfbe1048b41efbad0b691 && \
    git checkout d11c632ba8e972176f1bfbe1048b41efbad0b691

WORKDIR /workspace/vscode

# Create sanitized snapshot - removes git history but preserves file state
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for CSS validation
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
