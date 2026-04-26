FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip pkg-config libdbus-1-dev && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/uv && \
    cd /workspace/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 84a854c169ef8acdcc90692e40f6f540be74b956 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
