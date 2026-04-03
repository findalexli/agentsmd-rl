FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (zulip is a large monorepo)
RUN git init /workspace/zulip && \
    cd /workspace/zulip && \
    git remote add origin https://github.com/zulip/zulip.git && \
    git fetch --depth=1 origin f2946b9dd3ea604127f0213336704ae0e836319b && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/zulip

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
