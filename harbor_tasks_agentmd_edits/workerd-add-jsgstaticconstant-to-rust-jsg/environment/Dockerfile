FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — workerd is enormous)
RUN git init /workspace/workerd && \
    cd /workspace/workerd && \
    git remote add origin https://github.com/cloudflare/workerd.git && \
    git fetch --depth=1 origin 8a0534f6ac6363ee564dc1e6b22e6579786f22c3 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
