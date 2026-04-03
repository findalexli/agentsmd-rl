FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Enable corepack for Yarn Berry
RUN corepack enable

# Clone repo at base commit
RUN git init /workspace/storybook && \
    cd /workspace/storybook && \
    git remote add origin https://github.com/storybookjs/storybook.git && \
    git fetch --depth=1 origin 95aa11484a255b1c7f6227f2c81e2d441bb28988 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/storybook

# Install tsx globally for running TypeScript directly
RUN npm install -g tsx

# Install project deps (needed for running vitest upstream tests)
RUN yarn install 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
