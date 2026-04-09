FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# PostHog is a large monorepo — shallow fetch for speed
RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin 011a93306e5dfe5e26464fba7c61680076df62c8 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# No extra deps needed — tests use only stdlib (ast, unittest.mock)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
