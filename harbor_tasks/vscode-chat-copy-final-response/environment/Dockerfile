FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    libkrb5-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure git first (required before any git commit)
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

# Clone VS Code at base commit (snapshot without full history)
WORKDIR /workspace
ARG BASE_COMMIT=94c7bf8213beb59e3181fdb61992a032fc65e9a2
RUN git init vscode && cd vscode && \
    git remote add origin https://github.com/microsoft/vscode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && git add -A && git commit -m "snapshot"

# Install dependencies (VS Code requires npm install for tests)
WORKDIR /workspace/vscode
RUN npm install 2>&1 | tail -30 || true

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
