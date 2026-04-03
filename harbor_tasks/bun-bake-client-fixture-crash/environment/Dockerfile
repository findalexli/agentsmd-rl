FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone bun repo at base commit (before fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 923690e923b2f13e0815e8cf342748082058bede && \
    git checkout FETCH_HEAD

# Configure git for the agent
RUN cd /workspace/bun && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun