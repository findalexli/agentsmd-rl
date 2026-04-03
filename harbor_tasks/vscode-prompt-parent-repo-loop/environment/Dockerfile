FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/vscode

# Base commit: parent of merge commit ba1bdcd
ARG BASE_COMMIT=68cb51843c3f0f4e551479f825d18c954e88c778

# Clone VS Code at specific commit (shallow)
RUN git clone --depth=1 --no-checkout https://github.com/microsoft/vscode.git . && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install minimal dependencies for TypeScript compilation
RUN npm ci --ignore-scripts 2>/dev/null || npm install --legacy-peer-deps --ignore-scripts

# Sanitize: remove .git history, keep snapshot
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Create verifier logs directory
RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--max-old-space-size=4096"
WORKDIR /workspace/vscode
