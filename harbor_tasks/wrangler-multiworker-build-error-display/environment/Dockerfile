FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout d927ee342cd98932556c3671d7f2f01f30bcf954 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
