FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Zulip is large — use shallow clone via git init + fetch
RUN git init /workspace/zulip && \
    cd /workspace/zulip && \
    git remote add origin https://github.com/zulip/zulip.git && \
    git fetch --depth=1 origin a0fa7deed9a8c379055a2c896dcfebafa9ca1616 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/zulip

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
