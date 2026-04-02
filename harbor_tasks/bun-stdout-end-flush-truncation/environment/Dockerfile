FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git checkout ba05a72939569c1a371a513c3bd64a2cab6a60ee \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun