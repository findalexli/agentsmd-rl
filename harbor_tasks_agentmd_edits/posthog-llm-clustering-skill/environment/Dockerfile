FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --filter=blob:none for large monorepos)
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout d67b05b91702b8d6c5fcf03a1361d1afe7daf287 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
