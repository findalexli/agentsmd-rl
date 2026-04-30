FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# PostHog is a large monorepo — use depth limit for faster clone
RUN git clone --depth=1 https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git fetch --depth=1 origin 209f5d790aaee15baaf509ee15268edd932f5f23 && \
    git checkout 209f5d790aaee15baaf509ee15268edd932f5f23 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

ENV PYTHONPATH="/workspace/posthog"

# Install only what test_outputs.py needs — pyyaml for YAML parsing
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
