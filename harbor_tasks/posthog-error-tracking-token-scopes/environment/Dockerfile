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
    git fetch --depth=1 origin 43d0423b3f819335cfecfae1f1844ea883ba97ac && \
    git checkout 43d0423b3f819335cfecfae1f1844ea883ba97ac && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
