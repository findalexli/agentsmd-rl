FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sveltejs/svelte.git /workspace/svelte && \
    cd /workspace/svelte && \
    git checkout c93e251654a3193f294d6a4171d4087b4cb2fb80 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/svelte

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
