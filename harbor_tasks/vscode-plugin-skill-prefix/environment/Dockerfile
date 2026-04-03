FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv \
        pkg-config libx11-dev libxkbfile-dev libsecret-1-dev libkrb5-dev tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/vscode && \
    cd /workspace/vscode && \
    git remote add origin https://github.com/microsoft/vscode.git && \
    git fetch --depth=1 origin 559cb3e74d075670b9a03f84751e8fdcd3c52443 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/vscode

# Install dependencies (provides tsgo type checker and build tooling)
RUN npm install 2>&1 | tail -20

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
