FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed — storybook is a large monorepo)
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git /workspace/storybook && \
    cd /workspace/storybook && \
    git fetch --depth=1 origin 15180fa049e683c4a58d69615dde12e33456512c && \
    git checkout 15180fa049e683c4a58d69615dde12e33456512c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/storybook

# Enable corepack for Yarn Berry and install dependencies
RUN corepack enable && yarn install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
