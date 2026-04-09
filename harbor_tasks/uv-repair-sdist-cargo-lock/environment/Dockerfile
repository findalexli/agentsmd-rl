FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone — uv is large)
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout c5977cc4ae4cd1cf8b97c7193e927f7b2a9c4e87 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
