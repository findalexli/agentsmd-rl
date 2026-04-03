FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (storybook is a huge monorepo)
RUN git init /workspace/storybook && \
    cd /workspace/storybook && \
    git remote add origin https://github.com/storybookjs/storybook.git && \
    git fetch --depth=1 origin 5a9c6ecd7559ee8c7adbe30fb4b0894e369d144b && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/storybook

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
