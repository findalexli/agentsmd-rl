FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# PostHog is a large monorepo — partial clone (blobs lazy-fetched on demand)
RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin c68338921ad4d5598a9830cca90c9e1f34c2dc8f && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install pyyaml for YAML validation in tests
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
