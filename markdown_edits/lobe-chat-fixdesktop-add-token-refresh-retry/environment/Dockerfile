FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use filter=blob:none)
RUN git clone --filter=blob:none https://github.com/lobehub/lobe-chat.git /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git checkout 95bc5c2e6c9cca04b584002fbd85145e3b977e1f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
