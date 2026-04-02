FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone bun repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 5693fc1a98116743f16a7db2952d6e436bf9ec98

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun