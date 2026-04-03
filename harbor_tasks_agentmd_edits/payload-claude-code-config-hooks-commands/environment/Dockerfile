FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates jq tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (filtered for large monorepo)
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git checkout 80d7781b4f2fc2e874323532a0a8a8da65c8fc22 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
