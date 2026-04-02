FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone vscode at the pre-fix base commit (parent of merge commit)
ARG BASE_COMMIT=ba1bdcd30b83d8090ee0f28549299a52874d71ac
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="agent@example.com" -c user.name="Agent" commit -m "snapshot"

WORKDIR /workspace/vscode

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Ensure logs directory exists
RUN mkdir -p /logs/verifier
