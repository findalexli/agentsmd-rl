FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# VS Code is huge — use shallow snapshot
RUN git init /workspace/vscode && \
    cd /workspace/vscode && \
    git remote add origin https://github.com/microsoft/vscode.git && \
    git fetch --depth=1 origin 958f822bbea8a409fb7f6bc22cfc1594b61f61fd && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vscode

# No build deps needed — tests only read file content
RUN mkdir -p /logs/verifier
