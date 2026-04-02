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

# Clone vscode at the pre-fix base commit
ARG BASE_COMMIT=ee6bfc559a9089feb8b73962fd4fb5a306821ef4
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

# Install minimal TypeScript support for compilation checking
RUN npm install -g typescript@5.4.5

# Create verifier logs directory
RUN mkdir -p /logs/verifier
