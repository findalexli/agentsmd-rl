FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (blob-none filter for large monorepo)
RUN git clone --filter=blob:none https://github.com/cloudflare/workerd.git /workspace/workerd && \
    cd /workspace/workerd && \
    git checkout 13c36cb69dbfa695bb8862c0eb2b2a7c0be51d0e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
