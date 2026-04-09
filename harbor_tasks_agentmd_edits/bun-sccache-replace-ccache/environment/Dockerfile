FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates bash python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone bun repo at base commit (shallow to save time on large repo)
RUN git clone --filter=blob:none --single-branch https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 995d988c736293572f0a5a2c8a49fd1a2b6ca84c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
