FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vscode at the pre-fix base commit (shallow snapshot for speed)
ARG BASE_COMMIT=73b0fb29377f401a4e2b792b9065e77b9fa19e9e
RUN git clone --depth 1 https://github.com/microsoft/vscode.git /workspace/vscode && \
    cd /workspace/vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="agent@test" -c user.name="Agent" commit -m "snapshot"

WORKDIR /workspace/vscode

RUN git config --global user.email "agent@test" && \
    git config --global user.name "Agent"

# Install minimist for test harness (evaluates arg parsing from index.js)
RUN mkdir -p /opt/test-deps && cd /opt/test-deps && npm init -y --silent && npm install --silent minimist

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
