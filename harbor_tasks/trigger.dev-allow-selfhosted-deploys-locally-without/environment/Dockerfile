FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# trigger.dev is a huge monorepo — use shallow clone
RUN git init /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git remote add origin https://github.com/triggerdotdev/trigger.dev.git && \
    git fetch --depth=1 origin ad4daa3301f63354745cdcb8e911950d9fa5a93f && \
    git checkout ad4daa3301f63354745cdcb8e911950d9fa5a93f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
