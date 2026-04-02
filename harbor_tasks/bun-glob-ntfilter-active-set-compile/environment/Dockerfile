FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git checkout 39094877abb3e74557d3975dd015ee677220eb35

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun

# Configure git for patching
RUN git config user.email "test@test.com" && git config user.name "Test"