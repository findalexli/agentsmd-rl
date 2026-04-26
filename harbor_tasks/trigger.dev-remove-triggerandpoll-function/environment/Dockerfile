FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use filter for speed)
RUN git init /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git remote add origin https://github.com/triggerdotdev/trigger.dev.git && \
    git fetch --depth=1 origin 21c2c136beec90c28ec46c895561f5b3c258ec06 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
