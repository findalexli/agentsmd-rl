FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential cmake tmux && \
    rm -rf /var/lib/apt/lists/*

# Sparse checkout: only cmake/ + CONTRIBUTING.md + docs/project/
RUN git clone --filter=blob:none --sparse \
        https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git sparse-checkout set --no-cone 'cmake/*' 'CONTRIBUTING.md' 'docs/project/*' && \
    git checkout a14a89ca953910e89697895dfdfb4cdf4c90a151 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

RUN mkdir -p /logs/verifier
