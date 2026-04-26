FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/goose && \
    cd /workspace/goose && \
    git remote add origin https://github.com/block/goose.git && \
    git fetch --depth=1 origin e2d174ac1d4ed3304d9949f04572803467d343cb && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
