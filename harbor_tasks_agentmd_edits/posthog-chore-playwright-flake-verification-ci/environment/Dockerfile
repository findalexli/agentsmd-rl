FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip jq && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git clone --depth=1 https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git fetch --depth=1 origin e74eb42064ccff936e8b2039626646132a444c8d && \
    git checkout e74eb42064ccff936e8b2039626646132a444c8d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# PyYAML needed by test_outputs.py for YAML validation
RUN pip install --no-cache-dir --break-system-packages pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
