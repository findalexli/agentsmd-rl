FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for large monorepo)
RUN git clone --filter=blob:none https://github.com/cloudflare/workerd.git /workspace/workerd && \
    cd /workspace/workerd && \
    git checkout d7dc27c438f7ea1fd5eb28a0258d5dbae265a99d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
