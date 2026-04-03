FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone — playwright monorepo is very large
RUN mkdir -p /workspace/playwright && \
    cd /workspace/playwright && \
    git init && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 23b2c1599085bb6dad0f8fb916b631e3cb50ba4b && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
