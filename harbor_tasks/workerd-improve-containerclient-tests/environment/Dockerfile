FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/cloudflare/workerd.git /workspace/workerd && \
    cd /workspace/workerd && \
    git checkout e5eaa43c16c57bab977e5b53f4e57ca4418d084d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
