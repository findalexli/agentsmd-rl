FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

ENV BASE_COMMIT=d527672704494fd0cf3cc546dbcb259db37cc5ab

WORKDIR /tmp
RUN git clone --depth 1 https://github.com/microsoft/vscode.git /workspace/vscode && \
    cd /workspace/vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

WORKDIR /workspace/vscode

RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

RUN mkdir -p /logs/verifier
