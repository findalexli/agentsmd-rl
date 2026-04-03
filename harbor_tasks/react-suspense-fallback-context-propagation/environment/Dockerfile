FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN corepack enable

# Clone repo at base commit
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin f944b4c5352be02623d2d7415c0806350f875114 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/react

# Install dependencies for running tests
RUN yarn install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
