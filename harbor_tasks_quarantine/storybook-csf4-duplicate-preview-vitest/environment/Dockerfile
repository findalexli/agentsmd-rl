FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use blob filter)
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git /workspace/storybook && \
    cd /workspace/storybook && \
    git checkout 6d4fcb5417be0013e4c2d6e2e166a15a81637268 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/storybook

# Install TypeScript globally for AST-based test validation
RUN npm install -g typescript

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
