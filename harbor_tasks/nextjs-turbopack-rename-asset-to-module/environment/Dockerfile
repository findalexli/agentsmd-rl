FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (massive monorepo — blob filter)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/nextjs && \
    cd /workspace/nextjs && \
    git checkout d84e3bb56ecfdd9ff6ab5ee479e85be2780b8ba9 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/nextjs

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
