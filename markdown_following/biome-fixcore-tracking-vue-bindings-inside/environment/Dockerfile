FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone biome at base commit (large Rust monorepo — source only, no build)
RUN git init /workspace/biome && \
    cd /workspace/biome && \
    git remote add origin https://github.com/biomejs/biome.git && \
    git fetch --depth=1 origin c047e86583434beb33ed4fb0b49e627d26a8afbd && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
