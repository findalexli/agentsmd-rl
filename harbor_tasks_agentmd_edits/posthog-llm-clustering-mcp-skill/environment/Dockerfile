FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone PostHog at base commit (large monorepo — blob:none avoids downloading all file contents)
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout d67b05b91702b8d6c5fcf03a1361d1afe7daf287 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
