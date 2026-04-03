FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git remote add origin https://github.com/triggerdotdev/trigger.dev.git && \
    git fetch --depth=1 origin 6dfbe1d7628aefc894708a752d45aedb249ed5e7 && \
    git checkout 6dfbe1d7628aefc894708a752d45aedb249ed5e7 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
