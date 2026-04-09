FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PostHog/posthog.git /workspace/posthog && \
    cd /workspace/posthog && \
    git checkout 631f99184cf89fc8eef5163938c1a796a0e4af1b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
