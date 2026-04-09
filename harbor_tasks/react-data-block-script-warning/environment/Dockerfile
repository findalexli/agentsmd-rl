FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --depth=1 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin 4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3 && \
    git checkout 4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3 && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies (needed for running React's test suite)
RUN yarn install --frozen-lockfile 2>&1 || yarn install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

ENV NODE_ENV=test
