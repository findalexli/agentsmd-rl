FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large Rust monorepo — blob-none filter)
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout 4419f9cd39bd5951e2212342aa208fa479206f52 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
