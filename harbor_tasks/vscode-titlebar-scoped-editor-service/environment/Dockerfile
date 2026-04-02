FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (the buggy version that was reverted)
ARG BASE_COMMIT=bb01c58f40788bb80f069f73613f13c12af7566a
WORKDIR /workspace/vscode

RUN git clone --depth=50 https://github.com/microsoft/vscode.git . && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot (remove .git history to save space, init fresh)
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies needed for compilation
# TypeScript compilation only, no runtime testing needed
RUN npm ci || npm install

# Set up logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
