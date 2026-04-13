FROM python:3.12-slim
# For Node/TS repos: FROM node:22-slim  (add python3 for test runner)
# For Rust repos:    FROM rust:1.85-slim (add python3 for test runner)

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --depth=N for large monorepos)
RUN git clone --filter=blob:none https://github.com/anthropics/claude-code.git /workspace/claude-code && \
    cd /workspace/claude-code && \
    git checkout ae411f846195b38c8bec88914dd06132e00eadf8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/claude-code

# For Python repos: uncomment if tests import from the repo
# ENV PYTHONPATH="/workspace/claude-code"

# For Rust repos: pre-fetch deps for faster agent builds
# RUN cargo fetch && cargo check 2>&1 || true

# Install minimal deps needed by test_outputs.py (NOT full project deps)
# TODO: add only what test_outputs.py imports
# RUN pip install --no-cache-dir numpy ruff  # example

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
