FROM node:22-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=a48e9e3f10fed06c813399ccae8a28db7dd76683

# Clone repo at base commit (before the fix), sanitize snapshot
RUN git clone --depth=100 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin \"$BASE_COMMIT\" && \
    git checkout \"$BASE_COMMIT\" && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Configure git user for agent commits
RUN git config user.email "agent@test.com" && \
    git config user.name "Agent"

# No heavy deps needed — we only inspect and test the EventPluginUtils module
