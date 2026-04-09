FROM python:3.12-slim
# For Node/TS repos: FROM node:22-slim  (add python3 for test runner)
# For Rust repos:    FROM rust:1.85-slim (add python3 for test runner)

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux nix-bin cmake && \
    rm -rf /var/lib/apt/lists/*

# Enable Nix flakes and nix-command experimental features
RUN mkdir -p /etc/nix && \
    echo 'experimental-features = nix-command flakes' >> /etc/nix/nix.conf

# Clone repo at base commit (use --depth=N for large monorepos)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 6e3359dd16aced2f6fca2a8e2de71f09e0bcb3cb && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# For Python repos: uncomment if tests import from the repo
# ENV PYTHONPATH="/workspace/bun"

# For Rust repos: pre-fetch deps for faster agent builds
# RUN cargo fetch && cargo check 2>&1 || true

# Install minimal deps needed by test_outputs.py (NOT full project deps)
# TODO: add only what test_outputs.py imports
# RUN pip install --no-cache-dir numpy ruff  # example

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
