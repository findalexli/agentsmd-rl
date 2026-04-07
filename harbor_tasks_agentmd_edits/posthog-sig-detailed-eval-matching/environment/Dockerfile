FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# PostHog is a large monorepo — use sparse checkout for speed
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout 7b8a1992516a0218c75784e8d2c987f78118d400 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install only what test_outputs.py needs (numpy for cosine distance verification)
RUN pip install --no-cache-dir numpy

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
