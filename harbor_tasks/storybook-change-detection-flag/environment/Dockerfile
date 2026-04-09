FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed — storybook is a large monorepo)
RUN git init /workspace/storybook && \
    cd /workspace/storybook && \
    git remote add origin https://github.com/storybookjs/storybook.git && \
    git fetch --depth=1 origin 3f91f48ddcd1bb7cb7ee42a8b22229599317b796 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/storybook

RUN git config user.email "agent@test" && \
    git config user.name "Agent"

# Enable corepack for Yarn Berry and install dependencies
RUN corepack enable
RUN yarn install --immutable || yarn install || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
