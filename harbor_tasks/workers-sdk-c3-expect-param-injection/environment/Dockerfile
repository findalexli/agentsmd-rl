FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use blob filter)
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout f23c455ca2f762f0067ed0bfc810209ee3ab8323 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
