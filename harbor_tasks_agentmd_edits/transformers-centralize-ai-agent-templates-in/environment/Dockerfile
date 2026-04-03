FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential make tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed — transformers is huge)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 7cd2dd86ce3b2e598535f9aa1a40f79d6894f80a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
