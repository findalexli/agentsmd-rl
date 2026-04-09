FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow fetch — Deno is a large monorepo)
RUN git init /workspace/deno && \
    cd /workspace/deno && \
    git remote add origin https://github.com/denoland/deno.git && \
    git fetch --depth=1 origin d198cda44b7fddb56d892a8ef2349d1630adfa37 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
