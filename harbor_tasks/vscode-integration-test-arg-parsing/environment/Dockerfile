FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (vscode is enormous)
RUN git init /workspace/vscode && \
    cd /workspace/vscode && \
    git remote add origin https://github.com/microsoft/vscode.git && \
    git fetch --depth=1 origin 2de60eada57a6ea88a11ff72091e26b2825e84af && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vscode

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
