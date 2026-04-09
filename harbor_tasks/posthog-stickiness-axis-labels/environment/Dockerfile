FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Install typescript globally (for TS compiler API in tests)
RUN npm install -g typescript
ENV NODE_PATH=/usr/local/lib/node_modules

# Clone repo at base commit (shallow fetch — PostHog is large)
RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin 314b93aa807030d5ef1c9bb17d44cb3609f10cb3 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
