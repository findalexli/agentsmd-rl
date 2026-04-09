FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use --filter)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 3f41407f47eb009c654e45def5f3f67d6ce6c8ee && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

RUN mkdir -p /logs/verifier
