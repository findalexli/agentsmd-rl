FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# PostHog is a large monorepo — use depth limit
RUN git clone --depth=1 https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git fetch --depth=1 origin 12335b96f2209c3044a2fd623928284ab81b861d && \
    git checkout 12335b96f2209c3044a2fd623928284ab81b861d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install only what test_outputs.py needs (AST parsing + pytest)
# No Django or heavy deps needed — tests use AST and file content checks
RUN pip install --no-cache-dir pydantic

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
