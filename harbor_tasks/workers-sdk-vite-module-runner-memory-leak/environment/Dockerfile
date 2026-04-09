FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout 9fcdfca775d3d412abe7547d0833414599bab221 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
